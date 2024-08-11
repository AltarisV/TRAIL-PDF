import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    """
    Entry point for running the Flask application.

    - Creates the Flask application using the `create_app` function.
    - Opens the default web browser to the application's URL if running in the main process.
    - Starts the Flask development server on host `0.0.0.0` and port `7777` with debugging enabled.
    
    Environment Variables:
        WERKZEUG_RUN_MAIN (str): Used to check if the script is running in the main process to prevent the browser from opening twice.
    
    :returns: None
    """
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from app.utils.helpers import open_browser
        from threading import Timer
        Timer(1, open_browser).start()
    app.run(host='0.0.0.0', debug=True, port=7777)
