import base64
import os
import uuid
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_valid_image(file_stream):
    try:
        file_stream.seek(0)
        with Image.open(file_stream) as img:
            img.verify()
        file_stream.seek(0)
        return True
    except Exception as e:
        current_app.logger.error(f"Image validation error: {e}")
        return False


def save_image(image, temp_image_path):
    filename = secure_filename(image.filename)

    if not filename:
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4()) + ".jpg"

    if not os.path.exists(temp_image_path):
        os.makedirs(temp_image_path, exist_ok=True)

    image_path = os.path.join(temp_image_path, filename)
    image.save(image_path)

    return image_path


def delete_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)


def load_image(image_path):
    try:
        image = Image.open(image_path)
        current_app.logger.info(f"Image loaded successfully from {image_path}")
        return image
    except Exception as e:
        current_app.logger.error(f"Failed to load image: {e}")
        return None
