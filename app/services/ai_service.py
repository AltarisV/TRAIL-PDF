import os
import requests
import time
import csv
from flask import current_app
from app.services.image_service import encode_image
from app.utils.prompts import PROMPTS

# Define the directory for saving token usage logs
LOG_DIR = os.path.join(os.path.dirname(__file__), '../../logs/token_usage')
os.makedirs(LOG_DIR, exist_ok=True)  # Create the directory if it doesn't exist


def save_usage_to_csv(usage_info, filename="token_usage.csv"):
    filepath = os.path.join(LOG_DIR, filename)
    file_exists = os.path.isfile(filepath)
    with open(filepath, "a", newline='') as csvfile:
        fieldnames = ['prompt_tokens', 'completion_tokens', 'total_tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write the header only if the file doesn't exist

        writer.writerow(usage_info)


def send_image_to_ai(image_path, chosen_prompt):
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    prompt_text = PROMPTS.get(chosen_prompt)

    if prompt_text is None:
        current_app.logger.error(f"Unsupported language choice: {chosen_prompt}")
        return f"Error processing image. Unsupported language choice: {chosen_prompt}"

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
            usage_info = response_json.get('usage', {})

            save_usage_to_csv(usage_info)  # Save the token usage to a CSV file

            return text_content
        else:
            current_app.logger.error(
                f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image. API response status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Request to GPT API failed: {e}")
        return f"Error processing image. Exception: {e}"


def process_images_with_ai(images, chosen_prompt):
    texts = []
    for i, image in enumerate(images):
        if i > 0:
            time.sleep(2)
        current_app.logger.info(f"Processing image {image} on page {i + 1}")

        text = send_image_to_ai(image, chosen_prompt)

        current_app.logger.info(f"Received text: {text}")
        texts.append(text)
    return texts
