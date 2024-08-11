from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
import os
import shutil
from app.services.pdf_service import convert_pdf_to_images
from app.services.ai_service import process_images_with_ai
from app.utils.helpers import save_texts
from PyPDF2 import PdfReader

file_bp = Blueprint('file', __name__)


@file_bp.route('/files/<filename>')
def file_details(filename):
    """
    Displays details of a specific PDF file, including the number of pages.

    - Logs the access to the file details.
    - Attempts to read the PDF and count its pages.
    - Handles and logs errors during file processing.

    :param filename: The name of the PDF file.
    :type filename: str
    :returns:
        Response: Renders the 'file_details.html' template with the filename and page count.
        tuple: Error message and status code if an exception occurs.
    :rtype: flask.Response or tuple
    """
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
    """
    Converts an entire PDF to images and generates alt text using AI.

    :param filename: The name of the PDF file to convert.
    :type filename: str
    :returns:
        - If the conversion is successful, initiates the download of the generated HTML file with the alt text.
        - If an error occurs, redirects to the file details page.
    :rtype: flask.Response
    """
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    chosen_language = request.form.get('language', 'english')

    try:
        current_app.logger.info(f"Converting PDF to images for {file_path}")
        images = convert_pdf_to_images(file_path)
        current_app.logger.info(f"Images generated: {images}")

        texts = process_images_with_ai(images, chosen_language)

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
    """
    Converts a specified range of pages from a PDF to images and generates alt text using AI.

    - Logs the start of the conversion process.
    - Converts the specified range of PDF pages into images, processes them with AI, and saves the resulting text.
    - Handles and logs errors during the conversion process.

    :param filename: The name of the PDF file to convert.
    :type filename: str
    :returns:
        Response: A response that initiates the download of the generated HTML file with the alt text.
        Redirect: Redirects to the file details page if an error occurs.
    :rtype: flask.Response
    """
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

        texts = process_images_with_ai(images, chosen_language)

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
