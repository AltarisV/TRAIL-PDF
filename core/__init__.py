from flask import Flask
from config import Config
from dotenv import load_dotenv
import logging
import os


def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config)
    load_dotenv()

    # Set up logging
    logging.basicConfig(filename='app.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s '
                               '[in %(pathname)s:%(lineno)d]')
    app.logger.setLevel(logging.DEBUG)

    from core.routes.main_routes import main_bp
    from core.routes.file_routes import file_bp
    from core.routes.image_routes import image_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(image_bp)

    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])

    if not os.path.exists(app.config['TEMP_IMAGE_PATH']):
        os.makedirs(app.config['TEMP_IMAGE_PATH'])

    return app
