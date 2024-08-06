import io
import os
import webbrowser
import html
from flask import Response


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
    html_content += "<style>\n"
    html_content += "  .nav-list { list-style: none; padding: 0; }\n"
    html_content += "  .nav-list li { margin: 5px 0; }\n"
    html_content += "</style>\n"
    html_content += "</head>\n<body>\n"

    navigation = "<nav>\n  <ul class='nav-list'>\n"
    processed_content = ""
    for idx, text in enumerate(texts):
        processed_text, headers = process_text_for_html(text, idx)
        processed_content += processed_text + "\n\n"
        for header in headers:
            navigation += f'    <li><a href="#{header["id"]}">{header["title"]}</a></li>\n'
    navigation += "  </ul>\n</nav>\n"

    html_content += navigation
    html_content += processed_content

    html_content += "</body>\n</html>"
    html_bytes = io.BytesIO(html_content.encode('utf-8'))

    response = Response(html_bytes.getvalue(),
                        mimetype="text/html",
                        headers={"Content-Disposition": f"attachment;filename={new_filename}.html"})
    return response


def process_text_for_html(text, idx):
    lines = text.split('\n')
    processed_lines = []
    headers = []
    in_table = False
    in_code_block = False

    for line in lines:
        stripped_line = line.strip()

        # Handle <code> blocks without escaping
        if stripped_line.startswith("<code>"):
            in_code_block = True
            processed_lines.append(stripped_line)
        elif stripped_line.endswith("</code>") and in_code_block:
            processed_lines.append(stripped_line)
            in_code_block = False
        elif in_code_block:
            processed_lines.append(line)  # Do not escape the code block content

        # Handle <table> blocks without escaping
        elif stripped_line.startswith("<table"):
            in_table = True
            processed_lines.append(stripped_line)
        elif in_table and stripped_line.startswith("</table>"):
            in_table = False
            processed_lines.append(stripped_line)
        elif in_table:
            processed_lines.append(stripped_line)

        else:
            if not in_code_block:  # Escape only if not inside a code block
                line = escape_html(line)

            if line.startswith("Seite ") or line.startswith("Page "):
                colon_pos = line.find(':')
                if colon_pos != -1:
                    title_start_pos = line.find(',') + 1
                    title = line[title_start_pos:colon_pos].strip()
                    content = line[colon_pos + 1:].strip()

                    header_id = f"section-{idx}-{len(headers)}"
                    headers.append({"id": header_id, "title": title})

                    processed_lines.append(f'<h1 id="{header_id}">{title}</h1>')
                    if content:
                        processed_lines.append(f"<p>{content}</p>")
                else:
                    header_id = f"section-{idx}-{len(headers)}"
                    headers.append({"id": header_id, "title": line.strip()})
                    processed_lines.append(f'<h1 id="{header_id}">{line.strip()}</h1>')
            else:
                if line.strip():
                    processed_lines.append(f"<p>{line.strip()}</p>")

    return ''.join(processed_lines), headers


def escape_html(text):
    return html.escape(text)
