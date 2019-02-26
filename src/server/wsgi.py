from flask import Flask, abort, Response, send_file
from time import time


def get_status(name):
    return True


def create_app():
    app = Flask(__name__)

    types = set(['json', 'png'])
    platforms = ['hetarchief']

    @app.route('/ping')
    def ping():
        return 'pong'

    @app.route('/status/<name>.<type_>')
    def status_(name, type_):
        if type_ not in types:
            abort(404)

        if name not in platforms:
            abort(404)

        status = get_status(name)
        if type_ == 'png':
            file = 'static/status-' + ('ok' if status else 'nok') + '.png'
            return send_file(file, add_etags=False, last_modified=time(), cache_timeout=10)
        elif type_ == 'json':
            return Response('{"status": %d}' % (int(status)), mimetype='application/json')

        abort(500)  # shouldn't get here

    return app


application = create_app()

