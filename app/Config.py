import os
from dotenv import load_dotenv, set_key

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Configuration class for setting up environment variables and application settings.

    Attributes:
        SECRET_KEY (str): The secret key for session management.
        UPLOAD_EXTENSIONS (list): List of allowed file extensions for uploads.
        UPLOAD_PATH (str): Directory path for uploaded files.
        IMAGE_EXTENSIONS (list): List of allowed image file extensions.
        TEMP_IMAGE_PATH (str): Directory path for temporary images.
        OPENAI_API_KEY (str): API key for accessing OpenAI services.
        GPT_MODEL (str): The model name for the OpenAI GPT service.
        LOG_DIR (str): Directory path for saving application logs.
        TOKEN_USAGE_DIR (str): Directory path for saving token usage logs.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    UPLOAD_EXTENSIONS = ['.pdf']
    UPLOAD_PATH = os.path.join(base_dir, '..', 'uploads')
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    TEMP_IMAGE_PATH = os.path.join(base_dir, '..', 'temp_images')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GPT_MODEL = "gpt-4o"
    LOG_DIR = os.path.join(base_dir, '..', 'logs')
    TOKEN_USAGE_DIR = os.path.join(LOG_DIR, 'token_usage')

    @staticmethod
    def setup_env_file():
        """
        Sets up the .env file with necessary API keys.

        - Checks for required keys in the environment, such as 'OPENAI_API_KEY'.
        - If a key is missing, prompts the user to input the key value and updates the .env file.
        - Reloads the environment variables after setting the new key.

        :returns: None
        """
        env_file = os.path.join(base_dir, '..', '.env')
        load_dotenv(env_file)
        required_keys = ['OPENAI_API_KEY']

        for key in required_keys:
            if not os.getenv(key):
                value = input(f"Enter your {key}: ")
                set_key(env_file, key, value)
                # Update environment after setting new key
                os.environ[key] = value
