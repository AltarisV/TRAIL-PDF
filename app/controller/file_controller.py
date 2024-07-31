from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
import os
import shutil
from app.services.pdf_service import convert_pdf_to_images
from app.services.ai_service import process_images_with_gpt
from app.utils.helpers import save_texts
from PyPDF2 import PdfReader

file_bp = Blueprint('file', __name__)


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
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    chosen_language = request.form.get('language', 'english')

    try:
        current_app.logger.info(f"Converting PDF to images for {file_path}")
        images = convert_pdf_to_images(file_path)
        current_app.logger.info(f"Images generated: {images}")

        texts = process_images_with_gpt(images, chosen_language)

        flash('PDF successfully converted to alternative text.')
        current_app.logger.info(f"Conversion completed for {filename}")
        return save_texts(texts, filename, chosen_language)

    except Exception as e:
        flash(f'Error during conversion: {e}')
        current_app.logger.error(f"Error during conversion for {filename}: {e}")
        return redirect(url_for('file.file_details', filename=filename))
    finally:
        shutil.rmtree(current_app.config['TEMP_IMAGE_PATH'])


@file_bp.route('/convert_pdf_n_pages/<filename>', methods=['POST'])
def convert_pdf_n_pages(filename):
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    chosen_language = request.form.get('language', 'english')
    start_page = request.form.get('start_page', type=int, default=1)
    num_pages = request.form.get('num_pages', type=int)

    try:
        total_pages = len(PdfReader(file_path).pages)

        if not num_pages or num_pages <= 0 or start_page + num_pages - 1 > total_pages:
            num_pages = total_pages - start_page + 1

        end_page = min(start_page + num_pages - 1, total_pages)

        current_app.logger.info(
            f"Converting pages {start_page} to {end_page} of PDF to images for {file_path}")

        images = convert_pdf_to_images(file_path, start_page=start_page, end_page=end_page)
        current_app.logger.info(f"Images generated for pages {start_page} to {end_page}: {images}")

        texts = process_images_with_gpt(images, chosen_language)

        flash('PDF successfully converted to alternative text.')
        current_app.logger.info(f"Conversion completed for {filename}")
        base_name, file_extension = os.path.splitext(filename)
        modified_filename = f"{base_name}_pages_{start_page}_to_{end_page}{file_extension}"
        return save_texts(texts, modified_filename, chosen_language)

    except Exception as e:
        flash(f'Error during conversion: {e}')
        current_app.logger.error(f"Error during conversion for {filename}: {e}")
        return redirect(url_for('file.file_details', filename=filename))
    finally:
        shutil.rmtree(current_app.config['TEMP_IMAGE_PATH'])
