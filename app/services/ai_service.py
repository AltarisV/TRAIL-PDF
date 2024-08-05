import time
import torch
from flask import current_app
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from app.services.image_service import load_image
from app.utils.prompts import PROMPTS

# Globale Variablen für das Modell und den Prozessor
processor = None
model = None


def init_blip2_model():
    global processor, model
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b").to(
        "cuda" if torch.cuda.is_available() else "cpu")
    current_app.logger.info("BLIP-2 model and processor loaded successfully")


def send_image_to_ai(image_path, chosen_prompt):
    try:
        current_app.logger.info(f"Starting processing for image: {image_path}")

        # Load and prepare the image
        raw_image = load_image(image_path).convert('RGB')
        current_app.logger.info(f"Image loaded successfully from {image_path}")

        if chosen_prompt.lower() != "empty":
            prompt_text = PROMPTS.get(chosen_prompt)
            if prompt_text is None:
                current_app.logger.error(f"Unsupported language choice: {chosen_prompt}")
                return f"Error processing image. Unsupported language choice: {chosen_prompt}"

            current_app.logger.info(f"Using prompt: {prompt_text}")
            # Prepare inputs with the prompt
            inputs = processor(raw_image, prompt_text, return_tensors="pt").to(
                "cuda" if torch.cuda.is_available() else "cpu")
        else:
            # Prepare inputs without the prompt
            inputs = processor(raw_image, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

        current_app.logger.info(f"Inputs prepared for the model: {inputs}")

        # Perform prediction
        generated_ids = model.generate(**inputs, max_new_tokens=60, do_sample=True, temperature=0.7)
        current_app.logger.info(f"Output tensor from model: {generated_ids}")

        # Decode the output using batch_decode
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        current_app.logger.info(f"Model generated text: {generated_text}")

        return generated_text

    except Exception as e:
        current_app.logger.error(f"Error processing image with BLIP-2: {e}")
        return f"Error processing image. Exception: {e}"


def process_images_with_ai(images, chosen_prompt):
    texts = []
    for i, image_path in enumerate(images):
        if i > 0:
            time.sleep(2)
        current_app.logger.info(f"Processing image {i + 1} of {len(images)}: {image_path}")

        text = send_image_to_ai(image_path, chosen_prompt)

        if text:
            current_app.logger.info(f"Text successfully received for image {i + 1}: {text}")
        else:
            current_app.logger.warning(f"No text received for image {i + 1}")

        texts.append(text)

    current_app.logger.info("All images processed successfully")
    return texts
