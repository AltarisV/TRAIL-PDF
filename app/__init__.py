import os
import sys
from flask import Flask, request
from app.Config import Config
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from flask_babel import Babel


def set_working_directory():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(base_path)


def get_locale():
    # Check if the user has set a language preference in cookies
    lang = request.cookies.get('language')
    if lang in ['en', 'de']:
        return lang
    # Fallback to best match based on browser settings
    return request.accept_languages.best_match(['en', 'de'])


def create_app():
    """
    Creates and configures the Flask application.

    - Sets up environment variables and ensures API keys are loaded.
    - Configures logging to a rotating file handler.
    - Registers the application's blueprints.
    - Ensures necessary directories for file uploads, temporary images, and logs are created.

    :returns: The configured Flask application instance.
    :rtype: Flask
    """
    set_working_directory()  # Set the working directory
    Config.setup_env_file()

    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    load_dotenv()

    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'de']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'  # Adjust if translations directory is elsewhere

    babel = Babel(app, locale_selector=get_locale)

    @app.context_processor
    def inject_get_locale():
        return {'get_locale': get_locale}

    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])
    if not os.path.exists(app.config['TOKEN_USAGE_DIR']):
        os.makedirs(app.config['TOKEN_USAGE_DIR'])

    log_file_path = os.path.join(app.config['LOG_DIR'], 'app.log')
    file_handler = RotatingFileHandler(log_file_path, maxBytes=1024000, backupCount=25)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    # Test logging on startup
    app.logger.info('Logging has started.')

    from app.controller.main_controller import main_bp
    from app.controller.file_controller import file_bp
    from app.controller.image_controller import image_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(image_bp)

    app.logger.info('Blueprints registered.')

    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])

    if not os.path.exists(app.config['TEMP_IMAGE_PATH']):
        os.makedirs(app.config['TEMP_IMAGE_PATH'])

    app.logger.info('App successfully created.')
    return app
