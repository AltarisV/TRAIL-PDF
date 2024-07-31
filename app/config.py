import os
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    UPLOAD_EXTENSIONS = ['.pdf']
    UPLOAD_PATH = os.path.join(base_dir, '..', 'uploads')
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    TEMP_IMAGE_PATH = os.path.join(base_dir, '..', 'temp_images')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GPT_MODEL = "gpt-4o"
