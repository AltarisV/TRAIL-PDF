import base64
import os
import uuid
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime


def encode_image(image_path):
    """
    Encodes an image file into a Base64 string.

    :param image_path: The file path to the image.
    :type image_path: str
    :returns: The Base64 encoded string of the image.
    :rtype: str
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_valid_image(file_stream):
    """
    Validates whether a file stream contains a valid image.

    - Attempts to open the file stream as an image.
    - Verifies the integrity of the image file.

    :param file_stream: The file stream to validate.
    :type file_stream: file-like object
    :returns: True if the file is a valid image, False otherwise.
    :rtype: bool
    """
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
    """
    Saves an uploaded image to a temporary directory.

    - Generates a secure filename.
    - Creates the temporary directory if it doesn't exist.
    - Saves the image file to the specified path.

    :param image: The image file to save.
    :type image: FileStorage
    :param temp_image_path: The directory where the image will be saved.
    :type temp_image_path: str
    :returns: The file path where the image was saved.
    :rtype: str
    """
    filename = secure_filename(image.filename)

    if not filename:
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4()) + ".jpg"

    if not os.path.exists(temp_image_path):
        os.makedirs(temp_image_path, exist_ok=True)

    image_path = os.path.join(temp_image_path, filename)
    image.save(image_path)

    return image_path


def delete_image(image_path):
    """
    Deletes an image file if it exists.

    :param image_path: The file path to the image to be deleted.
    :type image_path: str
    :returns: None
    """
    if os.path.exists(image_path):
        os.remove(image_path)
