from flask import Flask, abort, Response, send_file, request, flash, session, render_template
from flask import url_for, redirect
from time import time
from viaastatus.prtg import api
from os import environ
import logging
from flask import jsonify
from configparser import ConfigParser
import re
import hmac
from hashlib import sha256
from functools import wraps, partial
import argparse
import itertools

log_level = logging._nameToLevel[environ.get('VERBOSITY', 'debug').upper()]
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(log_level)


class Responses:
    @staticmethod
    def json(obj):
        return jsonify(obj)

    @staticmethod
    def html(obj):
        return Response('<html><body>%s</body></html>' % (obj,), content_type='text/html')

    @staticmethod
    def txt(obj):
        if type(obj) is not str:
            obj = '\n'.join(obj)
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


def get_sensors(prtg) -> dict:
    sensors = {}
    cols = 'objid,name,device'
    ippattern = re.compile(r'[\d\.]+')
    for sensor in prtg.table(content='sensors',
                             filter_type=['http', 'ftp', 'httptransaction'],
                             filter_active=-1,
                             columns=cols)['sensors']:
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


def normalize(txt):
    txt = txt.replace(' ', '-').lower()
    txt = re.sub('-{2,}', '-', txt)
    txt = re.sub(r'\([^)]*\)', '', txt)
    txt = re.sub(r'\[[^)]*\]', '', txt)
    txt = re.sub('-[0-9]*$', '', txt)
    txt = re.sub('-{2,}', '-', txt)
    return txt


def create_app():
    app = Flask(__name__)

    config = ConfigParser()
    config.read(environ['CONFIG_FILE'])

    app_config = config['app']
    app.secret_key = app_config['secret_key']
    salt = app_config['salt']

    def _token(*args, **kwargs):
        """Calculates the token
        """
        params = str([args, kwargs])
        return hmac.new(salt.encode('utf-8'), params.encode('utf-8'), sha256).hexdigest()[2:10]

    def secured_by_login(func):
        """
        Decorator to define routes secured_by_login
        """

        @wraps(func)
        def _(*args, **kwargs):
            if not login_settings:
                logger.info('Login requested but refused since no login data in config')
                abort(404)

            if not session.get('authenticated'):
                return _login()

            return func(*args, **kwargs)
        return _

    def secured_by_token(func):
        """
        Decorator to define routes secured_by_token.
        """

        @wraps(func)
        def _(*args, **kwargs):
            check_token = 'authenticated' not in session
            if 'ignore_token' in kwargs:
                check_token = not kwargs['ignore_token']
                del kwargs['ignore_token']

            if check_token:
                token = request.args.get('token')
                expected_token = _token(*args, **kwargs)
                if token != expected_token:
                    logger.warning("Wrong token '%s' for %s, expected: '%s'", token, func.__name__, expected_token)
                    abort(401)
            return func(*args, **kwargs)

        _._secured_by_token = _token

        return _

    prtg = api.API.from_credentials(**config['prtg'])

    login_settings = None
    if config.has_section('login'):
        login_settings = dict(config['login'])

    class Choices:
        @staticmethod
        def sensor():
            return list(get_sensors(prtg).keys())

        @staticmethod
        def type_():
            return {'json', 'png', 'txt', 'html'}

        @staticmethod
        def ttype():
            return {'json', 'txt', 'html'}

    @app.route('/login', methods=['GET'])
    def _login():
        return render_template('login.html')

    @app.route('/urls', methods=['GET'])
    @secured_by_login
    def _urls():
        context = {}
        rules = [rule
                 for rule in application.url_map.iter_rules()
                 if rule.is_leaf
                 and rule.endpoint != 'static'
                 and not rule.endpoint.startswith('_')]
        method_types = {}
        for i in range(len(rules)):
            rule = rules[i]
            rules[i] = rules[i].__dict__
            kargs = [argname for argname in rule.arguments if hasattr(Choices, argname)]
            vargs = [getattr(Choices, argname)() for argname in kargs]

            methods = []
            for params in itertools.product(*vargs):
                params = dict(zip(kargs, params))
                url = url_for(rule.endpoint, **params)
                view_func = app.view_functions[rule.endpoint]
                if hasattr(view_func, '_secured_by_token'):
                    url += '?token=%s' % (view_func._secured_by_token(**params))
                methods.append({
                    "name": rule.endpoint,
                    "params": params,
                    "url": url,
                })
            method_types[rule.endpoint] = methods

        context['method_types'] = method_types
        return render_template('urls.html', **context)

    @app.route('/login', methods=['POST'])
    def _do_login():
        if not login_settings:
            logger.info('Login requested but refused since no login data in config')
            abort(404)

        if request.form['password'] != login_settings['password'] or \
           request.form['username'] != login_settings['username']:
            flash('Invalid credentials!')
        else:
            session['authenticated'] = True
        return redirect('/urls')

    @app.route('/', methods=['GET'])
    def index_():
        return render_template('oldstatus.html')

    @app.route('/sensors.<ttype>')
    @secured_by_token
    def sensors_(ttype):
        if ttype not in Choices.ttype():
            abort(404)

        return getattr(Responses, ttype)(Choices.sensor())

    @app.route('/status/<sensor>.<type_>', methods=['GET'])
    @secured_by_token
    def status_(sensor, type_):
        """
        :param str sensor: Name of the sensor
        :param str type_: Response type
        :return:
        """

        if type_ not in Choices.type_():
            abort(404)

        sensors = get_sensors(prtg)
        if sensor not in sensors:
            abort(404)

        sensor_id = sensors[sensor]
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
            status = status_msg % (sensor, sensor_id, status['statustext'])

        return getattr(Responses, type_)(status)

    # add aliases
    if config.has_section('aliases'):
        for url, target in config['aliases'].items():
            target = target.split(':')
            name = target.pop(0)
            func = app.view_functions[name]
            kwargs = dict(ignore_token=True)
            func = partial(func, *target, **kwargs)
            func.__name__ = url
            app.route(url)(func)

    return app


application = create_app()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action='store_true',
                        help='run in debug mode')
    parser.add_argument('--host',
                        help='hostname or ip to serve app')
    parser.add_argument('--port', type=int, default=1111,
                        help='port used by the server')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    application.run(host=args.host, port=args.port, debug=args.debug)

