import base64
from PIL import Image
from flask import current_app


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_valid_image(file_stream):
    try:
        file_stream.seek(0)
        with Image.open(file_stream) as img:
            img.verify()
        return True
    except Exception as e:
        current_app.logger.error(f"Image validation error: {e}")
        return False
