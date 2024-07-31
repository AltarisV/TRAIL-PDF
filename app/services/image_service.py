import base64
import requests
from flask import current_app
from PIL import Image


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_alt_text(image_path, prompt_type):
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['OPENAI_API_KEY']}"
    }

    if prompt_type == "mathematical":
        prompt_text = "Your mathematical prompt here."
    elif prompt_type == "table":
        prompt_text = "Your table prompt here."
    else:
        prompt_text = "Your normal prompt here."

    payload = {
        "model": current_app.config['GPT_MODEL'],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            text_content = response_json['choices'][0]['message']['content'] if response_json.get('choices') else ''
            return text_content
        else:
            print(f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image. API response status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"Request to GPT API failed: {e}")
        return f"Error processing image. Exception: {e}"

def is_valid_image(file_stream):
    try:
        file_stream.seek(0)
        with Image.open(file_stream) as img:
            img.verify()
        return True
    except Exception as e:
        current_app.logger.error(f"Image validation error: {e}")
        return False
