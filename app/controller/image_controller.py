from flask import Blueprint, request, jsonify, render_template, current_app
import os
import shutil
import uuid
from app.services.ai_service import send_image_to_ai
from app.services.image_service import save_image, delete_image, is_valid_image
from app.utils.prompts import PROMPTS

image_bp = Blueprint('image', __name__)


@image_bp.route('/image-upload')
def image_upload():
    """
    Renders the image upload page.

    :returns: The HTML page for image upload.
    :rtype: flask.Response
    """
    return render_template('image_upload.html')


@image_bp.route('/process-image', methods=['POST'])
def process_image():
    """
    Processes an uploaded image by sending it to the AI service and returns the generated alt text.

    - Validates the uploaded image.
    - Determines the appropriate prompt based on language and prompt type.
    - Saves the image temporarily in a unique subdirectory, processes it with AI, and deletes the subdirectory afterward.
    - Returns the generated alt text as a JSON response.

    :returns:
        - JSON response containing the alt text if successful.
        - JSON response with an error message and 400 status code if an error occurs.
    :rtype: flask.Response
    """
    if 'image' in request.files:
        image = request.files['image']
        prompt_type = request.form.get('prompt', 'standard')
        language = request.form.get('language', 'german')

        current_app.logger.info(f"Received image: {image.filename}")

        if not is_valid_image(image):
            return jsonify({"error": "Invalid image uploaded"}), 400

        # Determine the prompt key based on language and prompt type
        prompt_key = f"{prompt_type}_{language}"
        if prompt_key not in PROMPTS:
            current_app.logger.error(f"Unsupported prompt key: {prompt_key}")
            return jsonify({"error": f"Unsupported language or prompt type: {prompt_key}"}), 400

        # Unique subdirectory for this process to prevent race conditions
        temp_id = str(uuid.uuid4())
        unique_temp_path = os.path.join(current_app.config['TEMP_IMAGE_PATH'], temp_id)
        
        try:
            image_path = save_image(image, unique_temp_path)
            alt_text = send_image_to_ai(image_path, prompt_key)
            return jsonify(alt_text=alt_text)
        finally:
            if os.path.exists(unique_temp_path):
                shutil.rmtree(unique_temp_path)
    else:
        current_app.logger.error("No image uploaded")
        return jsonify({"error": "No image uploaded"}), 400
