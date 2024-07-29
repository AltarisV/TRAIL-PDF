import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    UPLOAD_EXTENSIONS = ['.pdf']
    UPLOAD_PATH = 'uploads'
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    TEMP_IMAGE_PATH = 'temp_images'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GPT_MODEL = "gpt-4o"
