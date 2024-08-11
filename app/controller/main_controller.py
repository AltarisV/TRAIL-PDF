from flask import Blueprint, render_template, current_app, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Displays the index page with a list of uploaded files.

    - Logs access to the index route.
    - Retrieves the list of files from the upload directory.
    - Renders the 'index.html' template with the list of files.

    :returns: The HTML page displaying the list of uploaded files.
    :rtype: flask.Response
    """
    current_app.logger.debug('Accessing index route')
    files = os.listdir(current_app.config['UPLOAD_PATH'])
    current_app.logger.debug(f'Files found: {files}')
    return render_template('index.html', files=files)


@main_bp.route('/', methods=['POST'])
def upload_files():
    """
    Handles the upload of files from the user.

    - Logs the start of the file upload process.
    - Validates and saves each uploaded file to the configured upload directory.
    - Logs errors for invalid file types.

    :returns: Redirects to the index page on success, or returns an error message and status code if the file type is invalid.
    :rtype: flask.Response or tuple
    """
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


@main_bp.route('/delete/<filename>')
def delete_file(filename):
    """
    Deletes a specified file.

    - Logs the deletion attempt.
    - Removes the file if it exists.
    - Logs any errors encountered during deletion.

    :param filename: The name of the file to delete.
    :type filename: str
    :returns: Redirects to the index page after the file is deleted.
    :rtype: flask.Response
    """
    current_app.logger.debug(f'Deleting file: {filename}')
    file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            current_app.logger.debug(f'File deleted: {file_path}')
    except Exception as e:
        current_app.logger.error(f'Error deleting file: {e}')
    return redirect(url_for('main.index'))
