import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from app.utils.helpers import open_browser
        from threading import Timer
        Timer(1, open_browser).start()
    app.run(host='0.0.0.0', debug=True, port=7777, use_reloader=False)
