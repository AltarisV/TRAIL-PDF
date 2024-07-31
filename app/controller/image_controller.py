from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.ai_service import send_image_to_gpt
from app.services.image_service import save_image, delete_image, is_valid_image

image_bp = Blueprint('image', __name__)


@image_bp.route('/image-upload')
def image_upload():
    return render_template('image_upload.html')


@image_bp.route('/process-image', methods=['POST'])
def process_image():
    TEMP_IMAGE_PATH = current_app.config['TEMP_IMAGE_PATH']
    if 'image' in request.files:
        image = request.files['image']
        prompt_type = request.form.get('prompt', 'normal')

        if not is_valid_image(image):
            return "Invalid image uploaded", 400

        image_path = save_image(image, TEMP_IMAGE_PATH)
        alt_text = send_image_to_gpt(image_path, prompt_type)
        delete_image(image_path)

        return jsonify(alt_text=alt_text)
    else:
        return "No image uploaded", 400
