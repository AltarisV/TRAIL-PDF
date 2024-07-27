from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from core.services.gpt_service import get_alt_text

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
        filename = secure_filename(image.filename)

        if not filename:
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4()) + ".jpg"

        if not os.path.exists(TEMP_IMAGE_PATH):
            os.makedirs(TEMP_IMAGE_PATH, exist_ok=True)

        image_path = os.path.join(TEMP_IMAGE_PATH, filename)
        image.save(image_path)

        alt_text = get_alt_text(image_path, prompt_type)

        if os.path.exists(image_path):
            os.remove(image_path)
        return jsonify(alt_text=alt_text)
    else:
        return "No image uploaded", 400
