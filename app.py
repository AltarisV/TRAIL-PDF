import io
import os
import sys
import time
import uuid
import webbrowser
from datetime import datetime
from threading import Timer

import openai
import base64
import requests
import fitz
from PIL.Image import Image
from PyPDF2 import PdfReader
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, current_app, Response, \
    jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, set_key


def setup_env_file():
    """Set up the .env file with necessary API keys."""
    env_file = '.env'
    load_dotenv(env_file)
    required_keys = ['OPENAI_API_KEY']

    for key in required_keys:
        if not os.getenv(key):
            value = input(f"Enter your {key}: ")
            set_key(env_file, key, value)


# Call this function at the start of your application
setup_env_file()

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
app_secret_key = "secretkey123"
openai.api_key = api_key
gpt_model = "gpt-4o"  # |"gpt-4-turbo"

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask('TRAIL', template_folder=template_folder)
else:
    app = Flask('TRAIL')

app.secret_key = app_secret_key
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']
app.config['UPLOAD_PATH'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])

TEMP_IMAGE_PATH = 'temp_images'
if not os.path.exists(TEMP_IMAGE_PATH):
    os.makedirs(TEMP_IMAGE_PATH)

app.config['IMAGE_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html', files=files)


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('file[]')
    for uploaded_file in uploaded_files:
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


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log the error here
        print(e)
    return redirect(url_for('index'))


@app.route('/image-upload')
def image_upload():
    return render_template('image_upload.html')


@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' in request.files:
        image = request.files['image']
        prompt_type = request.form.get('prompt', 'normal')  # Default to 'normal' if not specified
        filename = secure_filename(image.filename)

        # If no filename, generate one
        if not filename:
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4()) + ".jpg"

        image_path = os.path.join(TEMP_IMAGE_PATH, filename)
        image.save(image_path)

        # Use the combined function to get the alt text
        alt_text = get_alt_text(image_path, prompt_type)

        # Optionally delete the image file after processing
        os.remove(image_path)
        return jsonify(alt_text=alt_text)
    else:
        return "No image uploaded", 400


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

        # Send each image to the GPT model
        texts = []
        for i, image in enumerate(images):
            if i > 0:  # Introduce delay for all but the first image because of TPM (Tokens per Minute) Rate Limit
                time.sleep(6)  # Sleep for 6 seconds
            current_app.logger.info(f"Processing image {image} on page {i + 1}")

            if chosen_language == "english":
                text = send_image_to_gpt_english(image, page_number=i + 1)
            elif chosen_language == "german":
                text = send_image_to_gpt_german(image, page_number=i + 1)
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


@app.route('/convert_pdf_n_pages/<filename>', methods=['POST'])
def convert_pdf_n_pages(filename):
    current_app.logger.info(f"Starting conversion for {filename}")
    file_path = os.path.join(app.config['UPLOAD_PATH'], filename)

    # Retrieve the chosen language, starting page, and number of pages from the form data
    chosen_language = request.form.get('language', 'english')
    start_page = request.form.get('start_page', type=int)
    num_pages = request.form.get('num_pages', type=int)

    try:
        all_images = convert_pdf_to_images(file_path)
        total_pages = len(all_images)

        # If num_pages is not specified or invalid, default to converting to the end of the document
        if not num_pages or num_pages <= 0 or start_page + num_pages - 1 > total_pages:
            num_pages = total_pages - start_page + 1

        current_app.logger.info(f"Converting pages {start_page} to {start_page + num_pages - 1} of PDF to images for {file_path}")

        # Convert specified range of PDF pages to images
        end_page = min(start_page + num_pages - 1, total_pages)  # Ensure end page does not exceed total pages
        images = all_images[start_page-1:end_page]  # Adjust for zero-based indexing
        current_app.logger.info(f"Images generated for pages {start_page} to {end_page}: {images}")

        # Send each image to the GPT model
        texts = []
        for i, image in enumerate(images, start=start_page):
            if i > start_page:  # Introduce delay for all but the first image because of TPM (Tokens per Minute) Rate Limit
                time.sleep(6)  # Sleep for 6 seconds
            current_app.logger.info(f"Processing image {image} on page {i}")

            if chosen_language == "english":
                text = send_image_to_gpt_english(image, page_number=i)
            elif chosen_language == "german":
                text = send_image_to_gpt_german(image, page_number=i)
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
        base_name, file_extension = os.path.splitext(filename)
        modified_filename = f"{base_name}_pages_{start_page}_to_{end_page}{file_extension}"
        return save_texts(texts, modified_filename, chosen_language)

    except Exception as e:
        flash(f'Error during conversion: {e}')
        current_app.logger.error(f"Error during conversion for {filename}: {e}")
        return redirect(url_for('file_details', filename=filename))


def send_image_to_gpt_english(image_path, page_number):
    base64_image = encode_image(image_path)

    print(f"Sending image {image_path} to GPT API")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": gpt_model,
        "messages": [
            {
                "role": "user",
                # TODO Make GPT correctly put Markdown in the Response if they find it in the Image
                "content": [
                    {
                        "type": "text",
                        "text": "I am giving you an image from a university lecture slide."
                                "Your job is to generate a description that can be used as alternative text. "
                                "Give me a precise alternative text for the "
                                "shown illustrations. A student with total blindness should "
                                "be able to understand the illustrations. If you find any indications or associations,"
                                "make sure to detail them in your response. If there is text on the slide, "
                                "include the raw text in the alternative text, in english. If the original text on "
                                "the slide is not in english, only include the translated text in your response."
                                "If there are "
                                "mathematical formulas, include raw LaTeX markup for these formulas in the alternative "
                                "text without specifically outlining it. Also tell the mathematical formula in words"
                                "so that people who don't understand LaTeX can understand the formula. "
                                "On each of the slides, there is a footer at the bottom with the date "
                                "and other details. It is imperative that you write nothing about the slide footer or "
                                "its contents. Generally, write nothing about styling or design."
                                f"Your message must start with 'Page {page_number}, <a title in one-two words chosen "
                                f"on what is in the generated alternative text>:'. The title should be in english. "
                                f"Do not repeat the title in your alternative text for the slide. If you translate a "
                                f"title from another language, only include the translated title. Your response should "
                                f"only contain the Page, Title and the alternative text."
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
            print(f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image on page {page_number}. API response status: {response.status_code}"

    except requests.exceptions.RequestException as e:
        # Catch and log any exceptions during the API request
        print(f"Request to GPT API failed: {e}")
        return f"Error processing image on page {page_number}. Exception: {e}"


def send_image_to_gpt_german(image_path, page_number):
    base64_image = encode_image(image_path)

    print(f"Sending image {image_path} to GPT API")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": gpt_model,
        "messages": [
            {
                "role": "user",
                # TODO Make GPT correctly put Markdown in the Response if they find it in the Image
                "content": [
                    {"type": "text", "text": "Du sollst bei der Konvertierung in barrierefreie Unterlagen helfen und "
                                             "erstellst barrierefreie Inhalte. Ich gebe dir eine Vorlesungsfolie aus "
                                             "der Universität."
                                             "Generiere eine Beschreibung, die als Alternativtext genutzt werden kann. "
                                             "Gib mir einen präzisen Alternativtext für die "
                                             "gesamte Seite. Ein Studierender mit absoluter Blindheit sollte "
                                             "die Abbildung verstehen können. Falls du Assoziationen auf dem Bild "
                                             "erkennen kannst, beschreibe diese. Wenn normaler Text auf dem Bild "
                                             "zu erkennen ist, dann schreibe den Text ohne Änderung, aber auf deutsch, "
                                             "so auch in den Alternativtext. Wenn der originale Text nicht auf deutsch "
                                             "ist, dann sollte in deiner Antwort nur der übersetzte, deutsche Text "
                                             "vorkommen. "
                                             ""
                                             "Falls mathematische Formeln vorkommen, eine präzise "
                                             "Beschreibung dieser Formel in zugänglichem Text, als würde man sie vorlesen. "
                                             "( ist Klammer auf, ) ist Klammer zu, Wenn ein Bruch vorkommt musst du "
                                             "Zähler und Nenner als solche benennen. "
                                             "Ein Beispiel für eine zugängliche Formel ist: "
                                             "x Semikolon my Komma beta hoch minus 1 Endexponent "
                                             "istgleich Quadratwurzel aus Zähler beta geteilt durch Nenner 2 pi Bruchergebnis "
                                             "Wurzelende exp Klammer auf minus 1 halber Bruch "
                                             "beta linke Klammer x minus my rechte Klammer im Quadrat klammer zu. "
                                             ""
                                             "Wenn das Bild eine Tabelle beinhaltet, ist es deine Aufgabe, "
                                             "diese Tabelle in HTML Code umzuwandeln, damit es eine HTML-Tabelle wird, "
                                             "die ein blinder Student mit seinem Screenreader barrierefrei navigieren kann."
                                             "Deine Antwort sollte HTML-Code für die Tabelle beinhalten, "
                                             "sodass der Nutzer ihn kopieren und in seinem Dokument verwenden kann. Die Antwort sollte kein "
                                             "markdown beinhalten und möglichst mit border arbeiten."
                                             ""
                                             "Schreibe allgemein nichts über Styling, Design oder das Logo der Institution. "
                                             "Dies ist von höchster Wichtigkeit."
                                             "Deine Nachricht muss mit 'Seite {page_number}, <eine von dir generierte "
                                             "Überschrift in ein-zwei Worten>:' beginnen. Die Überschrift soll auf "
                                             "deutsch sein. Wiederhole in deiner Antwort nicht den Titel der Folie. "
                                             "Deine Antwort sollte nur die Seite, den Titel und "
                                             "den Alternativtext beinhalten."},
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
            print(f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}")
            return f"Error processing image on page {page_number}. API response status: {response.status_code}"

    except requests.exceptions.RequestException as e:
        # Catch and log any exceptions during the API request
        print(f"Request to GPT API failed: {e}")
        return f"Error processing image on page {page_number}. Exception: {e}"


def save_texts(texts, original_filename, language):
    base_filename = os.path.splitext(original_filename)[0]
    new_filename = base_filename + " " + language
    html_content = "<!DOCTYPE html>\n"
    # Construct the HTML content
    if language == "english":
        html_content += '<html lang="en">\n'
    elif language == "german":
        html_content += '<html lang="de">\n'
    else:
        html_content += '<html>\n'
    html_content += "<head>\n<meta charset=\"UTF-8\">\n"
    html_content += f"<title>{new_filename}</title>\n"
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
                        headers={"Content-Disposition": f"attachment;filename={new_filename}.html"})

    return response


def process_text_for_html(text):
    # Split the text into lines
    lines = text.split('\n')

    # Process each line
    processed_lines = []
    for line in lines:
        # Check if the line starts with "Seite " or "Page "
        if line.startswith("Seite ") or line.startswith("Page "):
            # Find the position of the colon
            colon_pos = line.find(':')
            if colon_pos != -1:
                # Extract the page number and title
                page_num_title = line[:colon_pos].strip()
                # Split page number and title
                page_num, title = page_num_title.split(',', 1)

                # Format the heading with the page number at the end
                processed_lines.append(f"<h1>{title.strip()} ({page_num.strip()})</h1>")

                # Extract and format the content, if any
                content = line[colon_pos + 1:].strip()
                if content:
                    processed_lines.append(f"<p>{content}</p>")
            else:
                # No colon found, treat the whole line as a header
                processed_lines.append(f"<h1>{line}</h1>")
        else:
            # If the line doesn't start with "Seite" and is not empty, add it as a paragraph
            if line.strip():
                processed_lines.append(f"<p>{line}</p>")

    # Join the processed lines back into a single string
    return ''.join(processed_lines)


def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF file to a list of images, with each image representing a page of the PDF.

    :param pdf_path: Path to the PDF file
    :return: List of images
    """
    try:
        doc = fitz.open(pdf_path)
        image_paths = []

        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            image_path = os.path.join(TEMP_IMAGE_PATH, f"page_{i + 1}.png")
            pix.save(image_path)
            image_paths.append(image_path)

        return image_paths  # This line should be outside the for-loop
    except Exception as e:
        current_app.logger.error(f"Error in convert_pdf_to_images: {e}")
        raise  # re-raise the exception to be caught in the calling function


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_valid_image(file_stream):
    try:
        # Reset the file stream's position to the beginning
        file_stream.seek(0)
        with Image.open(file_stream) as img:
            img.verify()  # Verify that it is, in fact, an image
        return True
    except Exception as e:
        current_app.logger.error(f"Image validation error: {e}")
        return False


def get_alt_text(image_path, prompt_type):
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    # Define prompts
    if prompt_type == "mathematical":
        prompt_text = ("Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie "
                       "Inhalte. "
                       "Ich gebe dir ein Bild von einer mathematischen Formel aus einer Vorlesungsfolie von der "
                       "Universität. Ich benötige eine präzise Beschreibung dieser Formel in zugänglichem Text, als "
                       "würde man sie vorlesen. Beispiel für eine zugängliche Formel: "
                       "''x Semikolon my Komma beta hoch minus 1 Endexponent"
                       "istgleich Quadratwurzel aus Zähler beta geteilt durch Nenner 2 pi Bruchergebnis "
                       "Wurzelende exp Klammer auf minus 1 halber Bruch"
                       "beta linke Klammer x minus my rechte Klammer im Quadrat klammer zu''."
                       "Außerdem benötige ich separat generiert rohes LaTeX für diese Formel. Deine Antwort sollte "
                       "in etwa so aufgebaut sein und direkt mit der Formel in zugänglichem Text anfangen: "
                       "{Formel in zugänglichem Text}"
                       "Formel in LaTeX: "
                       "{Formel in LaTeX}")  # Replace with your actual mathematical prompt
    elif prompt_type == "table":
        prompt_text = ("Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie "
                       "Inhalte. Ich gebe dir ein Bild von einer Tabelle aus einer Vorlesungsfolie an der Universität. "
                       "Deine Aufgabe ist es, diese Tabelle in HTML Code umzuwandeln, damit es eine HTML-Tabelle wird, "
                       "die ein blinder Student mit seinem Screenreader barrierefrei navigieren kann."
                       "Deine Antwort sollte ausschließlich den HTML-Code für die Tabelle beinhalten, "
                       "sodass der Nutzer ihn kopieren und in seinem Dokument verwenden kann. Die Antwort sollte kein "
                       "markdown beinhalten und möglichst mit border arbeiten.")
    elif prompt_type == "graph":
        prompt_text = ("Hier Text für Graphen einfügen")
    else: # normal
        prompt_text = ("Ich gebe dir ein Bild von einer Vorlesungsfolie aus der Universität."
                       "Generiere eine Beschreibung, die als Alternativtext genutzt werden kann. "
                       "Bitte gib mir einen präzisen Alternativtext für die "
                       "gezeigte Abbildung. Ein Studierender mit absoluter Blindheit sollte "
                       "die Abbildung verstehen können. Falls du Assoziationen auf dem Bild "
                       "erkennen kannst, beschreibe diese. Wenn normaler Text auf dem Bild "
                       "zu erkennen ist, dann schreibe den Text ohne Änderung, aber auf deutsch, "
                       "so auch in den Alternativtext. Wenn der originale Text nicht auf deutsch "
                       "ist, dann sollte in deiner Antwort nur der übersetzte, deutsche Text "
                       "vorkommen. Falls mathematische Formeln vorkommen, gib rohes LaTeX "
                       "für diese Formeln mit in deinen Alternativtext, ohne es "
                       "speziell hervorzuheben. Schreibe mathematische Formeln bitte zudem in "
                       "normaler Sprache auf, damit auch Leute, die kein LaTeX verstehen, die "
                       "Formel lesen können. Nimm auch konkrete Zusammenhänge "
                       "in den Alternativtext mit auf, falls welche vorhanden sind. "
                       "Deine Antwort sollte nur den Alternativtext beinhalten.")

    payload = {
        "model": gpt_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.2
    }

    print(f"Payload being sent to OpenAI API: {payload}")

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")

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


def open_browser():
    webbrowser.open_new('http://127.0.0.1:7777/')


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        Timer(1, open_browser).start()
    app.run(host='0.0.0.0', debug=True, port=7777)
