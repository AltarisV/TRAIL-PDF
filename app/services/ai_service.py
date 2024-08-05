import time
import torch
from flask import current_app
from PIL import Image
from transformers import InstructBlipProcessor, InstructBlipForConditionalGeneration
from app.services.image_service import load_image
from app.utils.prompts import PROMPTS

# Globale Variablen für das Modell und den Prozessor
processor = None
model = None
device = None


def init_blip2_model():
    global processor, model, device
    if model is None and processor is None:
        # Only initialize the model and processor if they are not already initialized
        model = InstructBlipForConditionalGeneration.from_pretrained("Salesforce/instructblip-vicuna-7b")
        processor = InstructBlipProcessor.from_pretrained("Salesforce/instructblip-vicuna-7b")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        current_app.logger.info("InstructBLIP model and processor loaded successfully")
    else:
        current_app.logger.info("InstructBLIP model and processor are already initialized")


def send_image_to_ai(image_path, chosen_prompt):
    try:
        current_app.logger.info(f"Starting processing for image: {image_path}")

        # Load and prepare the image
        raw_image = load_image(image_path).convert('RGB')
        current_app.logger.info(f"Image loaded successfully from {image_path}")

        # Check if a valid prompt is provided
        if chosen_prompt.lower() != "empty":
            # Retrieve the appropriate text prompt
            prompt_text = PROMPTS.get(chosen_prompt)
            if prompt_text is None:
                current_app.logger.error(f"Unsupported language choice: {chosen_prompt}")
                return f"Error processing image. Unsupported language choice: {chosen_prompt}"

            current_app.logger.info(f"Using prompt: {prompt_text}")
            # Prepare inputs with the prompt
            inputs = processor(images=raw_image, text=prompt_text, return_tensors="pt").to(device)
        else:
            # Prepare inputs without the prompt
            inputs = processor(images=raw_image, return_tensors="pt").to(device)

        current_app.logger.info(f"Inputs prepared for the model: {inputs}")
        outputs = model.generate(
            **inputs,
            do_sample=True,
            num_beams=5,
            max_length=2048,
            min_length=1,
            top_p=0.9,
            repetition_penalty=1.5,
            length_penalty=1.0,
            temperature=1,
        )
        generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
        current_app.logger.info(f"Model generated text: {generated_text}")

        return generated_text

    except Exception as e:
        current_app.logger.error(f"Error processing image with InstructBLIP: {e}")
        return f"Error processing image. Exception: {e}"


def process_images_with_ai(images, chosen_prompt):
    texts = []
    for i, image_path in enumerate(images):
        if i > 0:
            time.sleep(6)  # Optional: Sleep to add a delay between requests
        current_app.logger.info(f"Processing image {i + 1} of {len(images)}: {image_path}")

        text = send_image_to_ai(image_path, chosen_prompt)

        if text:
            current_app.logger.info(f"Text successfully received for image {i + 1}: {text}")
        else:
            current_app.logger.warning(f"No text received for image {i + 1}")

        texts.append(text)

    current_app.logger.info("All images processed successfully")
    return texts
