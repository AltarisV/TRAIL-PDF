PROMPTS = {
    'english': (
        "You are tasked with assisting in converting materials to accessible formats by creating accessible content. "
        "I am providing you with a university lecture slide. Generate a description that can be used as alternative text for the entire slide. "
        "A student with total blindness should be able to understand the illustration. Decorative elements should be ignored in your description. "
        "Accessibility is of utmost importance. If you recognize associations on the image, describe them. "
        "If normal text is visible on the image, write the text without changes, but in English, including it in the alternative text. "
        "If the original text is not in English, your response should only include the translated English text."
        "If your answer includes a list, the list should be in html."
        "\n\n"
        "If mathematical formulas are present, write a precise description of this formula in accessible text, as if it were being read aloud. "
        "Instead of '(' write 'open parenthesis,' and instead of ')' write 'close parenthesis.' If a fraction is present, you must name the numerator "
        "and denominator as such ('numerator one divided by denominator two equals 0.5'). An example of an accessible formula is: "
        "\"Sum from index 1 to n equals x semicolon mu comma beta raised to the power of minus 1 end exponent equals square root of numerator beta "
        "divided by denominator 2 pi fraction result root end exp open parenthesis minus one half fraction beta open parenthesis x minus mu close parenthesis "
        "squared close parenthesis.\""
        "\n\n"
        "If the image includes a table, it is your task to convert this table into HTML code, so that it becomes an HTML table that a blind student can navigate "
        "accessibly with their screen reader. Your response should include HTML code for the table with <thead>, <tbody> and <th scope> tags, along with a "
        "<caption> for the table. The response should not include markdown."
        "\n\n"
        "If the image contains code, it is your task to reproduce this code within an HTML <code> tag. Here is an example if the image contains code:\n"
        "<code>def hello_world():\n   print('hello world!')</code>"
        "\n\n"
        "Generally, write nothing about styling, design, or the institution's logo. This is of utmost importance. "
        "Your message must begin with 'Page {page_number}, <a title in one-two words generated by you>:' The title should be in English. "
        "Do not repeat the title of the slide in your response. Do NOT start your response with 'Alternative text:'."
    ),
    'german': (
        "Du sollst bei der Konvertierung in barrierefreie Unterlagen helfen und "
        "erstellst barrierefreie Inhalte. Ich gebe dir eine Vorlesungsfolie aus "
        "der Universität. Generiere eine Beschreibung, die als Alternativtext "
        "genutzt werden kann. Gib mir einen präzisen Alternativtext für die "
        "gesamte Seite. Ein Studierender mit absoluter Blindheit sollte "
        "die Abbildung verstehen können. Dekorative Elemente solltest du bei der Beschreibung ignorieren. "
        "Die Barrierefreiheit ist von oberster Wichtigkeit. Falls du Assoziationen auf dem Bild "
        "erkennen kannst, beschreibe diese. Wenn normaler Text auf dem Bild "
        "zu erkennen ist, dann schreibe den Text ohne Änderung, aber auf deutsch, "
        "so auch in den Alternativtext. Wenn der originale Text nicht auf deutsch "
        "ist, dann sollte in deiner Antwort nur der übersetzte, deutsche Text "
        "vorkommen. Wenn deine Antwort eine Aufzählung beinhaltet, verwende HTML für die Aufzählungen. "
        "Falls mathematische Formeln vorkommen,schreibe eine präzise "
        "Beschreibung dieser Formel in zugänglichem Text, als würde man sie vorlesen. "
        "Statt '(' schreibe Klammer auf, statt ')' schreibe Klammer zu. Wenn ein Bruch vorkommt, musst du "
        "Zähler und Nenner als solche benennen ('Zähler eins durch Nenner zwei istgleich 0,5'). "
        "Ein Beispiel für eine zugängliche Formel ist: "
        "Summe von Index 1 bis n istgleich x Semikolon my Komma beta hoch minus 1 Endexponent "
        "istgleich Quadratwurzel aus Zähler beta geteilt durch Nenner 2 pi Bruchergebnis "
        "Wurzelende exp Klammer auf minus 1 halber Bruch "
        "beta linke Klammer x minus my rechte Klammer im Quadrat klammer zu. "
        "Wenn das Bild eine Tabelle beinhaltet, ist es deine Aufgabe, "
        "diese Tabelle in HTML Code umzuwandeln, damit es eine HTML-Tabelle wird, "
        "die ein blinder Student mit seinem Screenreader barrierefrei navigieren kann. "
        "Deine Antwort sollte HTML-Code für die Tabelle beinhalten, mit <thead>, <tbody> und <th scope> tags"
        "sowie eine <caption> für die Tabellen. "
        "Die Antwort sollte kein markdown beinhalten. "
        "Wenn das Bild Code enthält, ist es deine Aufgabe, diesen Code in einem HTML-Code-Tag"
        " wiederzugeben, mit dem Tag <code>. Hier ist ein Beispiel, falls das Bild Code enthält: "
        "<code>def hello_world():"
        "   print.('hello world!')</code>"
        "Schreibe allgemein nichts über Styling, Design oder das Logo der Institution. "
        "Dies ist von höchster Wichtigkeit. "
        "Deine Nachricht muss mit 'Seite {page_number}, <eine von dir generierte "
        "Überschrift in ein-zwei Worten>:' beginnen. Die Überschrift soll auf "
        "deutsch sein. Wiederhole in deiner Antwort nicht den Titel der Folie. Ignoriere Quellenangaben. "
        "Starte deine Antwort NICHT mit 'Alternativtext:'."
    ),
    'bilingual': (
        "Du sollst bei der Konvertierung in barrierefreie Unterlagen helfen und "
        "erstellst barrierefreie Inhalte. Ich gebe dir eine Seite aus einem Sprachlehrbuch. "
        "Generiere eine Beschreibung, die als Alternativtext "
        "genutzt werden kann. Gib mir einen präzisen Text für die "
        "gesamte Seite. Ein Studierender mit absoluter Blindheit sollte "
        "die Seite verstehen können. Dekorative Elemente solltest du bei der Beschreibung ignorieren. "
        "Die Barrierefreiheit ist von oberster Wichtigkeit. Falls du Assoziationen auf dem Bild "
        "erkennen kannst, beschreibe diese. Der Text auf den Seiten ist entweder auf "
        "Wenn normaler Text auf dem Bild zu erkennen ist, dann schreibe den Text ohne Änderung "
        "in der jeweiligen Sprache so auch in den Alternativtext. Es ist imperativ, dass keine "
        "Informationen verloren gehen. Wenn das Bild eine Tabelle beinhaltet, ist es deine Aufgabe, "
        "diese Tabelle in HTML Code umzuwandeln, damit es eine HTML-Tabelle wird, "
        "die ein blinder Student mit seinem Screenreader barrierefrei navigieren kann. "
        "Deine Antwort sollte HTML-Code für die Tabelle beinhalten, "
        "sodass der Nutzer ihn kopieren und in seinem Dokument verwenden kann, sowie eine <caption> für diese. "
        "Vokabellisten sind als Tabellen zu behandeln."
        "Die Antwort darf kein Markdown beinhalten, nur HTML-Tags. "
        "Schreibe allgemein nichts über Styling, Design oder das Logo der Institution. "
        "Dies ist von höchster Wichtigkeit. "
        "Deine Nachricht muss mit 'Seite {page_number}, <eine von dir generierte "
        "Überschrift in ein-zwei Worten>:' beginnen. Wiederhole in deiner Antwort nicht den Titel der Folie. "
        "Starte deine Antwort NICHT mit 'Alternativtext:'."
    ),
    'mathematical_german': (
        "Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie Inhalte. "
        "Ich gebe dir ein Bild von einer mathematischen Formel aus einer Vorlesungsfolie von der Universität. "
        "Ich benötige eine präzise Beschreibung dieser Formel in zugänglichem Text, als würde man sie vorlesen. "
        "Beispiel für eine zugängliche Formel: ''x Semikolon my Komma beta hoch minus 1 Endexponent istgleich "
        "Quadratwurzel aus Zähler beta geteilt durch Nenner 2 pi Bruchergebnis Wurzelende exp Klammer auf minus 1 "
        "halber Bruch beta linke Klammer x minus my rechte Klammer im Quadrat klammer zu''. "
        "Außerdem benötige ich separat generiert rohes LaTeX für diese Formel. Starte deine Antwort NICHT mit "
        "'Alternativtext:'. Deine Antwort sollte in etwa so aufgebaut sein und direkt mit der Formel in zugänglichem "
        "Text anfangen: {Formel in zugänglichem Text} Formel in LaTeX: {Formel in LaTeX}"
    ),
    'table_german': (
        "Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie Inhalte. "
        "Ich gebe dir ein Bild von einer Tabelle aus einer Vorlesungsfolie an der Universität. "
        "Deine Aufgabe ist es, diese Tabelle in HTML-Code umzuwandeln, damit es eine HTML-Tabelle wird, die ein blinder "
        "Student mit seinem Screenreader barrierefrei navigieren kann. "
        "Deine Antwort sollte ausschließlich den HTML-Code für die Tabelle beinhalten, sodass der Nutzer ihn kopieren "
        "und in einem Dokument verwenden kann. Die Antwort sollte kein markdown beinhalten und möglichst mit border "
        "arbeiten. Starte deine Antwort NICHT mit 'Alternativtext:'."
    ),
    'code_german': (
        "Du sollst bei Konvertierung in barrierefreie Unterlagen helfen und erstellst barrierefreie Inhalte. "
        "Ich gebe dir ein Bild von einem Code-Ausschnitt aus einer Vorlesungsfolie an der Universität. "
        "Deine Aufgabe ist es, diesen Code als Code in einem HTML-Code-Tag wiederzugeben. Hier ist ein Beispiel: "
        "<code>def hello_world():"
        "   print.('hello world!')</code> "
        "Deine Antwort sollte ausschließlich den Code in einem HTML-Tag enthalten, sodass ein Nutzer ihn kopieren und "
        "in einem HTML-Dokument verwenden kann. Die Antwort sollte nur HTML-Code des im Bild dargestellten Codes "
        "beinhalten. Starte deine Antwort NICHT mit 'Alternativtext:'."
    ),
    'standard_german': (
        "Ich gebe dir ein Bild von einer Vorlesungsfolie aus der Universität. Generiere eine Beschreibung, die als "
        "Alternativtext genutzt werden kann. Bitte gib mir einen präzisen Alternativtext für die gezeigte Abbildung. "
        "Ein Studierender mit absoluter Blindheit sollte die Abbildung verstehen können. Falls du Assoziationen auf dem "
        "Bild erkennen kannst, beschreibe diese. Wenn normaler Text auf dem Bild zu erkennen ist, dann schreibe den Text "
        "ohne Änderung, aber auf deutsch, so auch in den Alternativtext. Wenn der originale Text nicht auf deutsch ist, "
        "dann sollte in deiner Antwort nur der übersetzte, deutsche Text vorkommen. Falls mathematische Formeln vorkommen, "
        "gib rohes LaTeX für diese Formeln mit in deinen Alternativtext, ohne es speziell hervorzuheben. Schreibe "
        "mathematische Formeln bitte zudem in normaler Sprache auf, damit auch Leute, die kein LaTeX verstehen, die Formel "
        "lesen können. Nimm auch konkrete Zusammenhänge in den Alternativtext mit auf, falls welche vorhanden sind. Deine "
        "Antwort sollte nur den Alternativtext beinhalten, starte deine Antwort NICHT mit 'Alternativtext:'."
    ),
    'mathematical_english': (
        "You are assisting in creating accessible materials by providing accessible content. "
        "I am giving you an image of a mathematical formula from a university lecture slide. "
        "I need a precise description of this formula in accessible text, as it would be read aloud. "
        "For example: 'x semicolon mu comma beta raised to the power of minus 1 end exponent is equal to "
        "the square root of the numerator beta divided by the denominator 2 pi fraction result square root end exp "
        "open parenthesis minus 1 half fraction beta left parenthesis x minus mu right parenthesis squared close parenthesis'. "
        "Additionally, I need the raw LaTeX for this formula separately. Start your response directly with the formula in accessible "
        "text and then provide the LaTeX: {Formula in accessible text} Formula in LaTeX: {Formula in LaTeX}"
    ),
    'table_english': (
        "You are assisting in creating accessible materials by providing accessible content. "
        "I am giving you an image of a table from a university lecture slide. "
        "Your task is to convert this table into HTML code, so it becomes an accessible HTML table that a blind student "
        "can navigate using their screen reader. Your response should only include the HTML code for the table, which can be "
        "copied and used in a document. The response should not include markdown and should use borders where possible. "
        "Start your response directly with the HTML code."
    ),
    'code_english': (
        "You are assisting in creating accessible materials by providing accessible content. "
        "I am giving you an image of a code snippet from a university lecture slide. "
        "Your task is to reproduce this code snippet within an HTML <code> tag. Here is an example: "
        "<code>def hello_world():"
        "   print('hello world!')</code>. "
        "Your response should only include the code within an HTML <code> tag so that it can be copied and used in an HTML document. "
        "The response should contain only the HTML code representation of the code snippet shown in the image."
    ),
    'standard_english': (
        "I am giving you an image of a university lecture slide. Generate a description that can be used as alternative text. "
        "Provide me with a precise alternative text for the image shown. A student with total blindness should be able to understand "
        "the image. If you find any associations in the image, describe them. If normal text is visible in the image, transcribe the "
        "text exactly as it appears, but in English. If the original text is not in English, only include the translated English text "
        "in your response. If there are mathematical formulas, provide raw LaTeX for those formulas without specifically highlighting it. "
        "Also describe mathematical formulas in plain language so that people who don't understand LaTeX can understand the formula. "
        "Include specific associations in the alternative text if any exist. Your response should only include the alternative text; do "
        "not start your response with 'Alternative text:'."
    )
}
