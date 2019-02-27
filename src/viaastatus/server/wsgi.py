from flask import Flask, abort, Response, send_file
from time import time
from viaastatus.prtg import api
from os import environ
import logging
from flask import jsonify
from configparser import ConfigParser
import re
import hmac
from hashlib import sha256
import base64
from functools import wraps

logging.basicConfig()
logger = logging.getLogger(__name__)


class Responses:
    @staticmethod
    def json(obj):
        return jsonify(obj)

    @staticmethod
    def html(obj):
        return Response('<html><body>%s</body></html>' % (obj,), content_type='text/html')

    @staticmethod
    def txt(obj):
        return Response(obj, content_type='text/plain')

    @staticmethod
    def file(file, **kwargs):
        if 'add_etags' not in kwargs:
            kwargs['add_etags'] = False

        if 'last_modified' not in kwargs:
            kwargs['last_modified'] = time()

        if 'cache_timeout' not in kwargs:
            kwargs['cache_timeout'] = 10
        return send_file(file, **kwargs)


def _checksum(*args, **kwargs):
    """Calculates the checksum
    """
    params = str([args, kwargs])
    return hmac.new(base64.b64decode(environ['SECRET']), params.encode('utf-8'), sha256).hexdigest()[:5]


def normalize(txt):
    txt = txt.replace(' ', '-').lower()
    txt = re.sub('-{2,}', '-', txt)
    txt = re.sub(r'\([^)]*\)', '', txt)
    txt = re.sub(r'\[[^)]*\]', '', txt)
    txt = re.sub('-[0-9]*$', '', txt)
    txt = re.sub('-{2,}', '-', txt)
    return txt


def get_sensors(prtg) -> dict:
    sensors = {}
    cols = 'objid,name,device'
    ippattern = re.compile(r'[\d\.]+')
    for sensor in prtg.table(content='sensors', filter_type='http', filter_active=-1, columns=cols)['sensors']:
        parentname = sensor['device']
        sensor_name = sensor['name']
        if sensor_name.startswith('HTTP'):
            # filter out IPs
            if ippattern.fullmatch(parentname):
                continue
            sensor_name = parentname + ' - ' + sensor_name
        sensor_name = normalize(sensor_name)

        if sensor_name in sensors:
            logger.warning("Sensor '%s' is conflicting (current id: %d, requested to set to: %d), ignored",
                           sensor_name,
                           sensors[sensor_name],
                           sensor['objid'])
            continue

        sensors[sensor_name] = int(sensor['objid'])
    return sensors


def checksummed(func):
    """
    Decorator to make calls checksummed.
    """

    @wraps(func)
    def _(checksum, *args, **kwargs):
        expected_checksum = _checksum(*args, **kwargs)
        if checksum != expected_checksum:
            logger.warning("Wrong checksum '%s' for %s, expected: '%s'", checksum, func.__name__, expected_checksum)
            abort(500)
        return func(*args, **kwargs)

    return _


def create_app():
    app = Flask(__name__)

    config = ConfigParser()
    config.read(environ['CONFIG_FILE'])

    prtg = api.API.from_credentials(**config['prtg'])

    types = set(['json', 'png', 'txt', 'html'])

    @app.route('/')
    def _():
        return 'IT WORKS!'

    @app.route('/sensors.<type_>')
    @checksummed
    def sensors(type_):
        return getattr(Responses, type_)(list(get_sensors(prtg).keys()))

    @app.route('/status/<name>.<checksum>.<type_>')
    @checksummed
    def status_(name, type_):
        if type_ not in types:
            abort(404)

        sensors = get_sensors(prtg)
        if name not in sensors:
            abort(404)

        sensor_id = sensors[name]
        status = prtg.getsensordetails(id=sensor_id)['sensordata']

        if type_ == 'png':
            img = 'nok'
            if int(status['statusid']) in [3, 4]:
                img = 'ok'
            elif int(status['statusid']) in [7, 8, 9, 10, 12]:
                img = 'unk'
            file = 'static/status-%s.png' % (img,)
            return Responses.file(file)

        if type_ == 'txt':
            status = status['statustext']
        elif type_ == 'html':
            status_msg = '''
            <dl>
                <dt>%s</dt>
                <dd><a href="https://do-mgm-mon-01.do.viaa.be/sensor.htm?id=%d">%s</a></dd>
            </dl>
            '''
            status = status_msg % (name, sensor_id, status['statustext'])

        return getattr(Responses, type_)(status)

    return app


application = create_app()

