import os
import sys
from dotenv import load_dotenv, set_key

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(base_dir, '_internal')
    env_file = os.path.join(internal_dir, '.env')
else:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_file = os.path.join(base_dir, '.env')

# Load the .env file if it exists
if os.path.exists(env_file):
    load_dotenv(env_file)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    UPLOAD_EXTENSIONS = ['.pdf']
    UPLOAD_PATH = os.path.join(base_dir, 'uploads')
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    TEMP_IMAGE_PATH = os.path.join(base_dir, 'temp_images')
    GPT_MODEL = "gpt-4o"
    LOG_DIR = os.path.join(base_dir, 'logs')
    TOKEN_USAGE_DIR = os.path.join(LOG_DIR, 'token_usage')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Ensure this is pulled from the environment

    @staticmethod
    def setup_env_file():
        """
        Sets up the .env file with necessary API keys.

        - Checks for required keys in the environment, such as 'OPENAI_API_KEY'.
        - If a key is missing, prompts the user to input the key value and updates the .env file.
        - Reloads the environment variables after setting the new key.

        :returns: None
        """
        required_keys = ['OPENAI_API_KEY']

        # Ensure the _internal directory exists
        os.makedirs(os.path.dirname(env_file), exist_ok=True)

        updated = False
        for key in required_keys:
            if not os.getenv(key):
                value = input(f"Enter your {key}: ")

                # Manually write the key to the .env file
                with open(env_file, 'a') as f:
                    f.write(f"{key}={value}\n")

                # Update environment after setting new key
                os.environ[key] = value
                updated = True
        if updated:
            # Reload the .env file to ensure the changes take effect in the current instance
            load_dotenv(env_file)

            # Update the Config class attributes with the newly loaded environment variables
            Config.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
