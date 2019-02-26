from flask import Flask, abort, Response, send_file
from time import time
from viaastatus.prtg import api
from os import environ
import logging
from flask import jsonify
from configparser import ConfigParser

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    config = ConfigParser()
    config.read(environ['CONFIG_FILE'])

    _ = config['prtg']
    prtg = api.API.from_credentials(_['host'], _['username'], _['password'])

    types = set(['json', 'png', 'txt'])

    @app.route('/status/<name>.<type_>')
    def status_(name, type_):
        if type_ not in types:
            abort(404)

        if name not in config['sensors']:
            abort(404)

        status = prtg.getsensordetails(config['sensors'][name])
        if type_ == 'png':
            img = 'nok'
            if int(status['statusid']) in [3, 4]:
                img = 'ok'
            elif int(status['statusid']) in [7, 8, 9, 10, 12]:
                img = 'unk'
            file = 'static/status-%s.png' % (img,)
            return send_file(file, add_etags=False, last_modified=time(), cache_timeout=10)
        elif type_ == 'json':
            return jsonify(status)
        elif type_ == 'txt':
            return Response(status['statustext'], content_type='text/plain')

        abort(500)  # shouldn't get here

    return app


application = create_app()

