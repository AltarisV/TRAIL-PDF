import io
import os
import time
import openai
import base64
import requests
from PyPDF2 import PdfReader
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, current_app, Response
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
app_secret_key = os.getenv('APP_SECRET_KEY')
openai.api_key = api_key
app = Flask(__name__)
app.secret_key = app_secret_key
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']
app.config['UPLOAD_PATH'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html', files=files)


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return "Invalid file type", 400
        file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        uploaded_file.save(file_path)

    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/files/<filename>')
def file_details(filename):
    file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
    try:
        with open(file_path, 'rb') as f:
            pdf = PdfReader(f)
            page_count = len(pdf.pages)
    except Exception as e:
        return f"Error processing file: {e}", 500

    return render_template('file_details.html', filename=filename, page_count=page_count)


@app.route('/convert_pdf/<filename>', methods=['POST'])
def convert_pdf(filename):
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(app.config['UPLOAD_PATH'], filename)

    # Retrieve the chosen language from the form data
    chosen_language = request.form.get('language', 'english')  # Default to English if not specified

    try:
        current_app.logger.info(f"Converting PDF to images for {file_path}")
        # Convert PDF to images
        images = convert_pdf_to_images(file_path)
        current_app.logger.info(f"Images generated: {images}")

        # Send each image to the GPT-4 vision model
        texts = []
        for i, image in enumerate(images):
            if i > 0:  # Introduce delay for all but the first image because of TPM (Tokens per Minute) Rate Limit
                time.sleep(6)  # Sleep for 6 seconds
            current_app.logger.info(f"Processing image {image} on page {i + 1}")

            if chosen_language == "english":
                text = send_image_to_gpt4_vision_english(image, page_number=i + 1)
            elif chosen_language == "german":
                text = send_image_to_gpt4_vision_german(image, page_number=i + 1)
            else:
                # Handle unexpected language choice
                current_app.logger.error(f"Unsupported language choice: {chosen_language}")
                flash(f'Unsupported language choice: {chosen_language}')
                return redirect(url_for('file_details', filename=filename))

            current_app.logger.info(f"Received text: {text}")
            texts.append(text)

        # Save the received texts

        flash('PDF successfully converted to alternative text.')
        current_app.logger.info(f"Conversion completed for {filename}")
        return save_texts(texts, filename, chosen_language)

    except Exception as e:
        flash(f'Error during conversion: {e}')
        current_app.logger.error(f"Error during conversion for {filename}: {e}")
        return redirect(url_for('file_details', filename=filename))

def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF file to a list of images, with each image representing a page of the PDF.

    :param pdf_path: Path to the PDF file
    :return: List of images
    """
    try:
        images = convert_from_path(pdf_path)

        # Save images to a temporary directory and return their file paths
        image_paths = []
        temp_dir = "temp_images"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        for i, image in enumerate(images):
            image_path = os.path.join(temp_dir, f"page_{i + 1}.jpg")
            image.save(image_path, 'JPEG')
            image_paths.append(image_path)

        return image_paths  # This line should be outside the for-loop
    except Exception as e:
        current_app.logger.error(f"Error in convert_pdf_to_images: {e}")
        raise  # re-raise the exception to be caught in the calling function


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def send_image_to_gpt4_vision_english(image_path, page_number):
    base64_image = encode_image(image_path)

    print(f"Sending image {image_path} to GPT-4 Vision API")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                # TODO Make GPT correctly put Markdown and LaTeX in the Response if they find it in the Image
                "content": [
                    {
                        "type": "text",
                        "text": "I am giving you an image from a university lecture slide."
                                "Generate a description that can be used as alternative text. "
                                "Please give me a short and precise alternative text for the "
                                "shown illustrations. A student with total blindness should "
                                "be able to understand the illustration. Please also include specific contexts "
                                "in the alternative text, if any are present. "
                                "On each of the slides, there is a green strip at the bottom with the date "
                                "and other details. Write nothing about these. Generally, "
                                "write nothing about styling or design."
                                f"Your message must start with 'Page {page_number}:'."
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.2
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Check if response is successful (status code 200)
        if response.status_code == 200:
            response_json = response.json()
            text_content = response_json['choices'][0]['message']['content'] if response_json.get('choices') else ''
            return text_content
        else:
            # Log error details if response is not successful
            print(f"Error from GPT-4 Vision API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image on page {page_number}. API response status: {response.status_code}"

    except requests.exceptions.RequestException as e:
        # Catch and log any exceptions during the API request
        print(f"Request to GPT-4 Vision API failed: {e}")
        return f"Error processing image on page {page_number}. Exception: {e}"


def send_image_to_gpt4_vision_german(image_path, page_number):
    base64_image = encode_image(image_path)

    print(f"Sending image {image_path} to GPT-4 Vision API")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                # TODO Make GPT correctly put Markdown and LaTeX in the Response if they find it in the Image
                "content": [
                    {"type": "text", "text": "Ich gebe dir ein Bild von einer Vorlesungsfolie aus der Universität."
                                             "Generiere eine Beschreibung, die als Alternativtext genutzt werden kann. "
                                             "Bitte gib mir einen kurzen und präzisen Alternativtext für die "
                                             "gezeigten Abbildungen. Ein Studierender mit absoluter Blindheit sollte "
                                             "die Abbildung verstehen können. Bitte nimm auch konkrete Zusammenhänge "
                                             "in den Alternativtext mit auf, falls welche vorhanden sind. "
                                             "Auf jeder der Folien ist unten ein grüner Streifen mit Datum "
                                             "und anderen Angaben. Schreibe nichts über diese. Schreibe allgemein "
                                             "nichts über styling oder design."
                                             f"Deine Nachricht muss mit 'Seite {page_number}:' beginnen."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Check if response is successful (status code 200)
        if response.status_code == 200:
            response_json = response.json()
            text_content = response_json['choices'][0]['message']['content'] if response_json.get('choices') else ''
            return text_content
        else:
            # Log error details if response is not successful
            print(f"Error from GPT-4 Vision API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image on page {page_number}. API response status: {response.status_code}"

    except requests.exceptions.RequestException as e:
        # Catch and log any exceptions during the API request
        print(f"Request to GPT-4 Vision API failed: {e}")
        return f"Error processing image on page {page_number}. Exception: {e}"


# TODO Save Text in a way that makes it more Screenreader friendly
#  Markdown for Code, LaTeX for mathematical stuff
def save_texts(texts, original_filename, language):
    html_content = "<!DOCTYPE html>\n"
    # Construct the HTML content
    if language == "english":
        html_content += '<html lang="en">\n'
    elif language == "german":
        html_content += '<html lang="de">\n'
    else:
        html_content += '<html>\n'
    html_content += "<head>\n<meta charset=\"UTF-8\">\n"
    html_content += f"<title>{original_filename}</title>\n"
    html_content += "</head>\n<body>\n"

    for text in texts:
        # Process each text block for HTML formatting
        processed_text = process_text_for_html(text)
        html_content += processed_text + "\n\n"

    html_content += "</body>\n</html>"

    # Convert the HTML content to a BytesIO object
    html_bytes = io.BytesIO(html_content.encode('utf-8'))

    # Create a response object and set the appropriate headers to prompt a download
    response = Response(html_bytes.getvalue(),
                        mimetype="text/html",
                        headers={"Content-Disposition": f"attachment;filename={original_filename}.html"})

    return response


def process_text_for_html(text):
    # Split the text into lines
    lines = text.split('\n')

    # Process each line
    processed_lines = []
    for line in lines:
        # Check if the line starts with "Seite "
        if line.startswith("Seite "):
            # Find the position of the colon
            colon_pos = line.find(':')
            if colon_pos != -1:
                # Extract and format the heading
                header = line[:colon_pos].strip()
                processed_lines.append(f"<h1>{header}</h1>")

                # Extract and format the content, if any
                content = line[colon_pos + 1:].strip()
                if content:
                    processed_lines.append(f"<p>{content}</p>")
            else:
                # No colon found, treat the whole line as a header
                processed_lines.append(f"<h1>{line}</h1>")
        else:
            # If the line doesn't start with "Seite", add it as a paragraph
            processed_lines.append(f"<p>{line}</p>")

    # Join the processed lines back into a single string
    return ''.join(processed_lines)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=7777)
