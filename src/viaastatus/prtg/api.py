import requests
import json

entrypoint = '/api'


class PRTGError(Exception):
    pass


class PRTGAuthenticationError(PRTGError):
    pass


class API:
    def __init__(self, host, username, passhash):
        self._host = host
        self._authparams = {
            "username": username,
            "passhash": passhash
        }

    def _get_url(self, method, response_type=None):
        if response_type is None:
            response_type = 'json'
        return '%s%s/%s.%s' % (self._host, entrypoint, method, response_type)

    def _call(self, method, params):
        url = self._get_url(method)
        try:
            params = dict(params, **self._authparams)
            response = requests.get(url, params)
            if response.status_code != 200:
                raise PRTGError("Invalid HTTP code response", response.status_code)
            response = json.loads(response.content.decode('utf-8'))
            return response
        except Exception as e:
            raise PRTGError(e)

    def getsensordetails(self, id_):
        response = self._call('getsensordetails', {"id": id_})
        return response['sensordata']

    @staticmethod
    def from_credentials(host, username, password):
        url = '%s%s/getpasshash.htm' % (host, entrypoint)

        params = {
            "username": username,
            "password": password,
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise PRTGAuthenticationError("Couldn't authenticate", response.status_code, response.content)
        return API(host, username, response.content)

