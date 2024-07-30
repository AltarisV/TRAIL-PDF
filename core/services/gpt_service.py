import requests
from flask import current_app
from core.utils.image_utils import encode_image


def send_image_to_gpt_english(image_path, page_number):
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    prompt_text = (
        f"Page {page_number}, <title>: "
        "I am giving you an image from a university lecture slide."
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
        "Your message must start with 'Page {page_number}, <a title in one-two words chosen "
        "on what is in the generated alternative text>:'. The title should be in english. "
        "Do not repeat the title in your alternative text for the slide. If you translate a "
        "title from another language, only include the translated title. Your response should "
        "only contain the Page, Title and the alternative text."
    )

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


def send_image_to_gpt_german(image_path, page_number):
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    prompt_text = (
        f"Seite {page_number}, <Überschrift>: "
        "Du sollst bei der Konvertierung in barrierefreie Unterlagen helfen und "
        "erstellst barrierefreie Inhalte. Ich gebe dir eine Vorlesungsfolie aus "
        "der Universität. Generiere eine Beschreibung, die als Alternativtext "
        "genutzt werden kann. Gib mir einen präzisen Alternativtext für die "
        "gesamte Seite. Ein Studierender mit absoluter Blindheit sollte "
        "die Abbildung verstehen können. Falls du Assoziationen auf dem Bild "
        "erkennen kannst, beschreibe diese. Wenn normaler Text auf dem Bild "
        "zu erkennen ist, dann schreibe den Text ohne Änderung, aber auf deutsch, "
        "so auch in den Alternativtext. Wenn der originale Text nicht auf deutsch "
        "ist, dann sollte in deiner Antwort nur der übersetzte, deutsche Text "
        "vorkommen. Falls mathematische Formeln vorkommen, eine präzise "
        "Beschreibung dieser Formel in zugänglichem Text, als würde man sie vorlesen. "
        "( ist Klammer auf, ) ist Klammer zu, Wenn ein Bruch vorkommt musst du "
        "Zähler und Nenner als solche benennen. "
        "Ein Beispiel für eine zugängliche Formel ist: "
        "x Semikolon my Komma beta hoch minus 1 Endexponent "
        "istgleich Quadratwurzel aus Zähler beta geteilt durch Nenner 2 pi Bruchergebnis "
        "Wurzelende exp Klammer auf minus 1 halber Bruch "
        "beta linke Klammer x minus my rechte Klammer im Quadrat klammer zu. "
        "Wenn das Bild eine Tabelle beinhaltet, ist es deine Aufgabe, "
        "diese Tabelle in HTML Code umzuwandeln, damit es eine HTML-Tabelle wird, "
        "die ein blinder Student mit seinem Screenreader barrierefrei navigieren kann. "
        "Deine Antwort sollte HTML-Code für die Tabelle beinhalten, "
        "sodass der Nutzer ihn kopieren und in seinem Dokument verwenden kann. Die Antwort sollte kein "
        "markdown beinhalten und möglichst mit border arbeiten. "
        "Schreibe allgemein nichts über Styling, Design oder das Logo der Institution. "
        "Dies ist von höchster Wichtigkeit. "
        "Deine Nachricht muss mit 'Seite {page_number}, <eine von dir generierte "
        "Überschrift in ein-zwei Worten>:' beginnen. Die Überschrift soll auf "
        "deutsch sein. Wiederhole in deiner Antwort nicht den Titel der Folie. "
        "Deine Antwort sollte nur die Seite, den Titel und "
        "den Alternativtext beinhalten. Starte den Alternativtext NICHT mit 'Alternativtext:'."
    )

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
    base64_image = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{base64_image}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['OPENAI_API_KEY']}"
    }

    if prompt_type == "mathematical":
        prompt_text = (
            "Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie Inhalte. "
            "Ich gebe dir ein Bild von einer mathematischen Formel aus einer Vorlesungsfolie von der Universität. "
            "Ich benötige eine präzise Beschreibung dieser Formel in zugänglichem Text, als würde man sie vorlesen. "
            "Beispiel für eine zugängliche Formel: ''x Semikolon my Komma beta hoch minus 1 Endexponent istgleich "
            "Quadratwurzel aus Zähler beta geteilt durch Nenner 2 pi Bruchergebnis Wurzelende exp Klammer auf minus 1 "
            "halber Bruch beta linke Klammer x minus my rechte Klammer im Quadrat klammer zu''. "
            "Außerdem benötige ich separat generiert rohes LaTeX für diese Formel. Starte deine Antwort NICHT mit "
            "'Alternativtext:'. Deine Antwort sollte in etwa so aufgebaut sein und direkt mit der Formel in zugänglichem "
            "Text anfangen: {Formel in zugänglichem Text} Formel in LaTeX: {Formel in LaTeX}")
    elif prompt_type == "table":
        prompt_text = (
            "Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie Inhalte. "
            "Ich gebe dir ein Bild von einer Tabelle aus einer Vorlesungsfolie an der Universität. "
            "Deine Aufgabe ist es, diese Tabelle in HTML Code umzuwandeln, damit es eine HTML-Tabelle wird, die ein blinder "
            "Student mit seinem Screenreader barrierefrei navigieren kann. "
            "Deine Antwort sollte ausschließlich den HTML-Code für die Tabelle beinhalten, sodass der Nutzer ihn kopieren "
            "und in seinem Dokument verwenden kann. Die Antwort sollte kein markdown beinhalten und möglichst mit border "
            "arbeiten. Starte deine Antwort NICHT mit 'Alternativtext:'.")
    else:
        prompt_text = (
            "Ich gebe dir ein Bild von einer Vorlesungsfolie aus der Universität. Generiere eine Beschreibung, die als "
            "Alternativtext genutzt werden kann. Bitte gib mir einen präzisen Alternativtext für die gezeigte Abbildung. "
            "Ein Studierender mit absoluter Blindheit sollte die Abbildung verstehen können. Falls du Assoziationen auf dem "
            "Bild erkennen kannst, beschreibe diese. Wenn normaler Text auf dem Bild zu erkennen ist, dann schreibe den Text "
            "ohne Änderung, aber auf deutsch, so auch in den Alternativtext. Wenn der originale Text nicht auf deutsch ist, "
            "dann sollte in deiner Antwort nur der übersetzte, deutsche Text vorkommen. Falls mathematische Formeln vorkommen, "
            "gib rohes LaTeX für diese Formeln mit in deinen Alternativtext, ohne es speziell hervorzuheben. Schreibe "
            "mathematische Formeln bitte zudem in normaler Sprache auf, damit auch Leute, die kein LaTeX verstehen, die Formel "
            "lesen können. Nimm auch konkrete Zusammenhänge in den Alternativtext mit auf, falls welche vorhanden sind. Deine "
            "Antwort sollte nur den Alternativtext beinhalten, starte deine Antwort NICHT mit 'Alternativtext:'.")

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
