import os
from dotenv import load_dotenv, set_key

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # secret key not relevant for local use
    UPLOAD_EXTENSIONS = ['.pdf']
    UPLOAD_PATH = os.path.join(base_dir, '..', 'uploads')
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    TEMP_IMAGE_PATH = os.path.join(base_dir, '..', 'temp_images')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GPT_MODEL = "gpt-4o"

    @staticmethod
    def setup_env_file():
        # Set up the .env file with necessary API keys
        env_file = os.path.join(base_dir, '..', '.env')
        load_dotenv(env_file)
        required_keys = ['OPENAI_API_KEY']

        for key in required_keys:
            if not os.getenv(key):
                value = input(f"Enter your {key}: ")
                set_key(env_file, key, value)
                # Update environment after setting new key
                os.environ[key] = value
