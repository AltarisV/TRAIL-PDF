import fitz
import os
import shutil
from flask import current_app


def convert_pdf_to_images(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        image_paths = []

        if os.path.exists(current_app.config['TEMP_IMAGE_PATH']):
            shutil.rmtree(current_app.config['TEMP_IMAGE_PATH'])
        os.makedirs(current_app.config['TEMP_IMAGE_PATH'], exist_ok=True)

        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            image_path = os.path.join(current_app.config['TEMP_IMAGE_PATH'], f"page_{i + 1}.png")
            pix.save(image_path)
            image_paths.append(image_path)

        return image_paths
    except Exception as e:
        current_app.logger.error(f"Error in convert_pdf_to_images: {e}")
        raise
