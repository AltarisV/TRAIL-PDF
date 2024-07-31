import requests
from flask import current_app
from app.services.image_service import encode_image
from app.utils.prompts import PROMPTS


def send_image_to_gpt(image_path, prompt_type):
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    prompt_text = PROMPTS.get(prompt_type)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['OPENAI_API_KEY']}"
    }

    payload = {
        "model": current_app.config['GPT_MODEL'],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_url}}
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
            current_app.logger.error(
                f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image. API response status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Request to GPT API failed: {e}")
        return f"Error processing image. Exception: {e}"


def get_alt_text(image_path, prompt_type):
    return send_image_to_gpt(image_path, prompt_type)
