from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
import os
import shutil
import uuid
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
    Converts a PDF (full or partial) to images and generates alt text using AI.
    """
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    chosen_language = request.form.get('language', 'english')
    
    # Page range parameters
    start_page = request.form.get('start_page', type=int, default=1)
    num_pages = request.form.get('num_pages', type=int)

    # Unique temp directory to prevent race conditions
    temp_id = str(uuid.uuid4())
    output_dir = os.path.join(current_app.config['TEMP_IMAGE_PATH'], temp_id)

    try:
        total_pages = len(PdfReader(file_path).pages)
        
        # Validation
        if start_page < 1:
            start_page = 1
        if start_page > total_pages:
            flash(f'Start page {start_page} exceeds total pages {total_pages}.')
            return redirect(url_for('file.file_details', filename=filename))

        if not num_pages or num_pages <= 0 or start_page + num_pages - 1 > total_pages:
            end_page = total_pages
        else:
            end_page = start_page + num_pages - 1

        current_app.logger.info(f"Converting pages {start_page} to {end_page} of PDF for {file_path}")
        images = convert_pdf_to_images(file_path, output_dir, start_page=start_page, end_page=end_page)
        
        texts = process_images_with_ai(images, chosen_language)

        flash('PDF successfully converted to alternative text.')
        current_app.logger.info(f"Conversion completed for {filename}")
        
        if start_page == 1 and end_page == total_pages:
            download_filename = filename
        else:
            base_name, ext = os.path.splitext(filename)
            download_filename = f"{base_name}_pages_{start_page}_to_{end_page}{ext}"
            
        return save_texts(texts, download_filename, chosen_language)

    except Exception as e:
        flash(f'Error during conversion: {e}')
        current_app.logger.error(f"Error during conversion for {filename}: {e}")
        return redirect(url_for('file.file_details', filename=filename))
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


@file_bp.route('/convert_pdf_n_pages/<filename>', methods=['POST'])
def convert_pdf_n_pages(filename):
    """Deprecated route, redirected to convert_pdf"""
    return convert_pdf(filename)

