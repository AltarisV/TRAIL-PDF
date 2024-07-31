from flask import Blueprint, render_template, current_app, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    current_app.logger.debug('Accessing index route')
    files = os.listdir(current_app.config['UPLOAD_PATH'])
    current_app.logger.debug(f'Files found: {files}')
    return render_template('index.html', files=files)


@main_bp.route('/', methods=['POST'])
def upload_files():
    current_app.logger.debug('Uploading files')
    uploaded_files = request.files.getlist('file[]')
    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                current_app.logger.error(f'Invalid file type: {file_ext}')
                return "Invalid file type", 400
            file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
            uploaded_file.save(file_path)
            current_app.logger.debug(f'File saved: {file_path}')

    return redirect(url_for('main.index'))


@main_bp.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename)


@main_bp.route('/delete/<filename>')
def delete_file(filename):
    current_app.logger.debug(f'Deleting file: {filename}')
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            current_app.logger.debug(f'File deleted: {file_path}')
    except Exception as e:
        current_app.logger.error(f'Error deleting file: {e}')
    return redirect(url_for('main.index'))
