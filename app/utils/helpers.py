import io
import os
import webbrowser

from dotenv import load_dotenv, set_key
from flask import Response


def setup_env_file():
    env_file = '.env'
    load_dotenv(env_file)
    required_keys = ['OPENAI_API_KEY']

    for key in required_keys:
        if not os.getenv(key):
            value = input(f"Enter your {key}: ")
            set_key(env_file, key, value)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:7777/')


def save_texts(texts, original_filename, language):
    base_filename = os.path.splitext(original_filename)[0]
    new_filename = base_filename + " " + language
    html_content = "<!DOCTYPE html>\n"

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
        processed_text = process_text_for_html(text)
        html_content += processed_text + "\n\n"

    html_content += "</body>\n</html>"
    html_bytes = io.BytesIO(html_content.encode('utf-8'))

    response = Response(html_bytes.getvalue(),
                        mimetype="text/html",
                        headers={"Content-Disposition": f"attachment;filename={new_filename}.html"})
    return response


def process_text_for_html(text):
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if line.startswith("Seite ") or line.startswith("Page "):
            colon_pos = line.find(':')
            if colon_pos != -1:
                title_start_pos = line.find(',') + 1
                title = line[title_start_pos:colon_pos].strip()
                content = line[colon_pos + 1:].strip()

                processed_lines.append(f"<h1>{title}</h1>")
                if content:
                    processed_lines.append(f"<p>{content}</p>")
            else:
                processed_lines.append(f"<h1>{line}</h1>")
        else:
            if line.strip():
                processed_lines.append(f"<p>{line}</p>")
    return ''.join(processed_lines)
