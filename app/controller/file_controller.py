from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash, jsonify, Response, \
    stream_with_context, send_file
import os
import shutil
from app.services.pdf_service import convert_pdf_to_images
from app.services.ai_service import process_images_with_ai, send_image_to_ai
from app.utils.helpers import save_texts
from PyPDF2 import PdfReader
import time

file_bp = Blueprint('file', __name__)

# Global variable to track progress and output file path
progress = 0
output_file_path = ""  # Global variable to store the output file path


@file_bp.route('/files/<filename>')
def file_details(filename):
    current_app.logger.debug(f'Accessing file details for: {filename}')
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    try:
        with open(file_path, 'rb') as f:
            pdf = PdfReader(f)
            page_count = len(pdf.pages)
        current_app.logger.debug(f'Page count for {filename}: {page_count}')
    except Exception as e:
        current_app.logger.error(f'Error processing file: {e}')
        return f"Error processing file: {e}", 500

    return render_template('file_details.html', filename=filename, page_count=page_count)


@file_bp.route('/convert_pdf/<filename>', methods=['POST'])
def convert_pdf(filename):
    global progress, output_file_path  # Use the global variables
    progress = 0
    output_file_path = ""
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    chosen_language = request.form.get('language', 'english')

    def generate():
        global progress, output_file_path  # Use the global variables
        try:
            current_app.logger.info(f"Converting PDF to images for {file_path}")
            images = convert_pdf_to_images(file_path)
            progress_step = 100 // len(images)

            texts = []
            for i, image in enumerate(images):
                if i > 0:
                    time.sleep(2)
                current_app.logger.info(f"Processing image {image} on page {i + 1}")

                text = send_image_to_ai(image, chosen_language)

                current_app.logger.info(f"Received text: {text}")
                texts.append(text)
                progress += progress_step
                yield f"data: {progress}\n\n"

            flash('PDF successfully converted to alternative text.')
            current_app.logger.info(f"Conversion completed for {filename}")
            response, output_file_path = save_texts(texts, filename, chosen_language)
            yield f"data: 100\n\n"

        except Exception as e:
            flash(f'Error during conversion: {e}')
            current_app.logger.error(f"Error during conversion for {filename}: {e}")
            yield f"data: error\n\n"
            return redirect(url_for('file.file_details', filename=filename))
        finally:
            shutil.rmtree(current_app.config['TEMP_IMAGE_PATH'])
            progress = 100  # Set progress to 100 when done

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@file_bp.route('/convert_pdf_n_pages/<filename>', methods=['POST'])
def convert_pdf_n_pages(filename):
    global progress, output_file_path  # Use the global variables
    progress = 0
    output_file_path = ""
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    chosen_language = request.form.get('language', 'english')
    start_page = request.form.get('start_page', type=int, default=1)
    num_pages = request.form.get('num_pages', type=int)

    def generate(num_pages):
        global progress, output_file_path  # Use the global variables
        try:
            total_pages = len(PdfReader(file_path).pages)

            if not num_pages or num_pages <= 0 or start_page + num_pages - 1 > total_pages:
                num_pages = total_pages - start_page + 1

            end_page = min(start_page + num_pages - 1, total_pages)

            current_app.logger.info(
                f"Converting pages {start_page} to {end_page} of PDF to images for {file_path}")

            images = convert_pdf_to_images(file_path, start_page=start_page, end_page=end_page)
            progress_step = 100 // len(images)

            texts = []
            for i, image in enumerate(images):
                if i > 0:
                    time.sleep(2)
                current_app.logger.info(f"Processing image {image} on page {i + 1}")
                text = send_image_to_ai(image, chosen_language)
                current_app.logger.info(f"Received text: {text}")
                texts.append(text)
                progress += progress_step
                yield f"data: {progress}\n\n"

            flash('PDF successfully converted to alternative text.')
            current_app.logger.info(f"Conversion completed for {filename}")
            base_name, file_extension = os.path.splitext(filename)
            modified_filename = f"{base_name}_pages_{start_page}_to_{end_page}{file_extension}"
            output_file_path = \
            save_texts(texts, modified_filename, chosen_language).headers["Content-Disposition"].split("filename=")[1]
            yield f"data: 100\n\n"

        except Exception as e:
            flash(f'Error during conversion: {e}')
            current_app.logger.error(f"Error during conversion for {filename}: {e}")
            yield f"data: error\n\n"
            return redirect(url_for('file.file_details', filename=filename))
        finally:
            shutil.rmtree(current_app.config['TEMP_IMAGE_PATH'])
            progress = 100  # Set progress to 100 when done

    return Response(stream_with_context(generate(num_pages)), mimetype='text/event-stream')


@file_bp.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    global output_file_path
    current_app.logger.info(f"Attempting to download file: {output_file_path}")
    if output_file_path and os.path.exists(output_file_path):
        return send_file(output_file_path, as_attachment=True)
    else:
        current_app.logger.error(f'File {output_file_path} not found.')
        flash(f'File {filename} not found.')
        return redirect(url_for('file.file_details', filename=filename))


@file_bp.route('/progress_endpoint/<filename>')
def progress_endpoint(filename):
    global progress  # Use the global variable

    def generate():
        while progress < 100:
            yield f"data: {progress}\n\n"
            time.sleep(1)
        yield f"data: 100\n\n"

    return Response(generate(), mimetype='text/event-stream')


@file_bp.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(progress=progress)
