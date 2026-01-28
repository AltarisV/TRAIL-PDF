import io
import os
import webbrowser
import html
from flask import Response
from collections import defaultdict
import re


def open_browser():
    """
    Opens the default web browser and navigates to the local server URL.

    :returns: None
    """
    webbrowser.open_new('http://127.0.0.1:7777/')


def save_texts(texts, original_filename, language):
    """
    Saves processed text content as an HTML file with navigation links.

    - Creates an HTML document with language-specific settings.
    - Adds a navigation bar based on the headers found in the texts.
    - Saves the content to a temporary file and prepares it for download.

    :param texts: A list of text strings to be processed and saved.
    :type texts: list of str
    :param original_filename: The original name of the file to base the new filename on.
    :type original_filename: str
    :param language: The language setting to be used in the HTML document (e.g., 'english', 'german').
    :type language: str
    :returns: A Flask Response object that initiates a download of the generated HTML file.
    :rtype: flask.Response
    """
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

    # Dictionary to count duplicate headers
    header_counter = defaultdict(int)

    navigation = "<nav>\n  <ul class='nav-list'>\n"
    processed_content = ""
    for idx, text in enumerate(texts):
        processed_text, headers = process_text_for_html(text, idx, header_counter)
        
        for header in headers:
            # Add to navigation
            navigation += f'    <li><a href="#{header["id"]}">{header["title"]}</a></li>\n'

        processed_content += processed_text + "\n\n"

    navigation += "  </ul>\n</nav>\n"

    html_content += navigation
    html_content += processed_content

    html_content += "</body>\n</html>"
    html_bytes = io.BytesIO(html_content.encode('utf-8'))

    response = Response(html_bytes.getvalue(),
                        mimetype="text/html",
                        headers={"Content-Disposition": f"attachment;filename={new_filename}.html"})
    return response


def process_text_for_html(text, idx, header_counter=None):
    """
    Processes a text string into HTML content, identifying and structuring headers and paragraphs.
    """
    if header_counter is None:
        header_counter = defaultdict(int)

    lines = text.split('\n')
    processed_lines = []
    headers = []
    in_code_block = False
    in_table = False

    # If the final line includes any of these tags, skip escaping:
    NON_ESCAPED_TAGS = [
        "<table", "</table>", "<tr>", "</tr>", "<th>", "</th>", "<td>", "</td>",
        "<caption>", "</caption>", "<thead>", "</thead>", "<tbody>", "</tbody>",
        "<ul>", "</ul>", "<li>", "</li>", "<ol>", "</ol>",
        "<strong>", "</strong>", "<em>", "</em>", "<p>", "</p>"
    ]

    for line in lines:
        stripped_line = line.strip()

        # 1) If we detect a <code> block start
        if "<code>" in stripped_line and not in_code_block:
            in_code_block = True
            processed_lines.append("<pre><code>")
            code_start_index = stripped_line.find("<code>") + len("<code>")
            # Escape any code segment to avoid injection
            processed_lines.append(html.escape(stripped_line[code_start_index:]))

        # 2) If we detect a Code block end
        elif "</code>" in stripped_line and in_code_block:
            code_end_index = stripped_line.find("</code>")
            processed_lines.append(html.escape(stripped_line[:code_end_index]))
            processed_lines.append("</code></pre>")
            in_code_block = False

        # 3) If we're inside a code block, keep escaping
        elif in_code_block:
            processed_lines.append(html.escape(line))
            processed_lines.append("\n")

        else:
            # First, run markdown on the line (handle **bold**, *italic*, etc.)
            converted_line = markdown_to_html(line)

            # If line has any of the recognized tags => skip escaping
            if any(tag in converted_line for tag in NON_ESCAPED_TAGS):
                # If line might contain <table>, track that for your in_table logic
                if "<table" in converted_line:
                    in_table = True
                if "</table>" in converted_line:
                    in_table = False

                processed_line = converted_line

            # If we're within a table but haven't detected new tags
            elif in_table:
                processed_line = converted_line
                if "</table>" in converted_line:
                    in_table = False

            else:
                # Default: escape the final line
                processed_line = html.escape(converted_line)

            # Now see if line starts with "Seite ..." or "Page ...":
            # If so, treat as a new <h1> block
            if processed_line.startswith("Seite ") or processed_line.startswith("Page ") or processed_line.startswith("ページ ") or processed_line.startswith("Sayfa ") or processed_line.startswith("Page ") :
                colon_pos = processed_line.find(':')
                if colon_pos != -1:
                    # Grab the text after 'Seite 1,' etc. as the header
                    title_start_pos = processed_line.find(',') + 1
                    title = processed_line[title_start_pos:colon_pos].strip()
                    content = processed_line[colon_pos + 1:].strip()

                    header_counter[title] += 1
                    display_title = f"{title} {header_counter[title]}" if header_counter[title] > 1 else title
                    
                    header_id = f"section-{idx}-{len(headers)}-{header_counter[title]}"
                    headers.append({"id": header_id, "title": display_title})

                    processed_lines.append(f'<h1 id="{header_id}">{display_title}</h1>')
                    if content:
                        processed_lines.append(f"<p>{content}</p>")
                else:
                    # No colon => entire line is the header
                    title = processed_line.strip()
                    header_counter[title] += 1
                    display_title = f"{title} {header_counter[title]}" if header_counter[title] > 1 else title
                    
                    header_id = f"section-{idx}-{len(headers)}-{header_counter[title]}"
                    headers.append({"id": header_id, "title": display_title})
                    processed_lines.append(f'<h1 id="{header_id}">{display_title}</h1>')

            else:
                # Not a "Seite" line
                if processed_line.strip():
                    processed_lines.append(f"<p>{processed_line.strip()}</p>")

    return "".join(processed_lines), headers


def markdown_to_html(text):
    """
    Converts basic Markdown syntax to HTML.

    :param text: Text containing Markdown syntax.
    :type text: str
    :returns: Text with Markdown replaced by HTML.
    :rtype: str
    """
    # Replace **bold** with <strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Replace *italic* with <em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    return text


def escape_html(text):
    """
    Escapes special HTML characters in a text string to prevent injection attacks.

    :param text: The text to escape.
    :type text: str
    :returns: The escaped text.
    :rtype: str
    """
    return html.escape(text)
