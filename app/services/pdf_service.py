import os
import shutil
from flask import current_app
import fitz


def convert_pdf_to_images(pdf_path, start_page=None, end_page=None):
    """
    Converts a PDF document into individual image files for each page.

    - Opens the PDF document and converts each page within the specified range to a PNG image.
    - Saves the images to a temporary directory specified in the application's configuration.

    :param pdf_path: The file path to the PDF document that needs to be converted.
    :type pdf_path: str
    :param start_page: The page number to start conversion (1-based index). Defaults to the first page.
    :type start_page: int, optional
    :param end_page: The page number to end conversion (1-based index). Defaults to the last page.
    :type end_page: int, optional
    :returns: A list of file paths to the generated PNG images.
    :rtype: list of str
    :raises Exception: If an error occurs during the PDF conversion process, the exception is logged and re-raised.
    """
    try:
        doc = fitz.open(pdf_path)
        image_paths = []

        if os.path.exists(current_app.config['TEMP_IMAGE_PATH']):
            shutil.rmtree(current_app.config['TEMP_IMAGE_PATH'])
        os.makedirs(current_app.config['TEMP_IMAGE_PATH'], exist_ok=True)

        start_page = start_page - 1 if start_page else 0
        end_page = end_page if end_page else len(doc)

        for i in range(start_page, end_page):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            image_path = os.path.join(current_app.config['TEMP_IMAGE_PATH'], f"page_{i + 1}.png")
            pix.save(image_path)
            image_paths.append(image_path)

        return image_paths
    except Exception as e:
        current_app.logger.error(f"Error in convert_pdf_to_images: {e}")
        raise
