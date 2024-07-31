from flask import Flask
from app.config import Config  # Import aus dem 'app' Ordner
from dotenv import load_dotenv
import logging
import os
from logging.handlers import RotatingFileHandler


def create_app():
    app = Flask(__name__, template_folder='templates')  # Aktualisierter Pfad für Templates
    app.config.from_object(Config)
    load_dotenv()

    # Set up logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    # Test logging on startup
    app.logger.info('Flask application has started')

    from app.controller.main_controller import main_bp  # Aktualisierte Importe
    from app.controller.file_controller import file_bp
    from app.controller.image_controller import image_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(image_bp)

    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])

    if not os.path.exists(app.config['TEMP_IMAGE_PATH']):
        os.makedirs(app.config['TEMP_IMAGE_PATH'])

    return app
