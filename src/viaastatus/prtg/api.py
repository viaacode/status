import requests
import json
import functools
import logging
# from collections import defaultdict
# from xml.etree import ElementTree


# ref: https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
# def etree_to_dict(t):
#     d = {t.tag: {} if t.attrib else None}
#     children = list(t)
#     if children:
#         dd = defaultdict(list)
#         for dc in map(etree_to_dict, children):
#             for k, v in dc.items():
#                 dd[k].append(v)
#         d = {t.tag: {k: v[0] if len(v) == 1 else v
#                      for k, v in dd.items()}}
#     if t.attrib:
#         d[t.tag].update(('@' + k, v)
#                         for k, v in t.attrib.items())
#     if t.text:
#         text = t.text.strip()
#         if children or t.attrib:
#             if text:
#                 d[t.tag]['#text'] = text
#         else:
#             d[t.tag] = text
#     return d


logger = logging.getLogger(__name__)


entrypoint = '/api'


class PRTGError(Exception):
    pass


class PRTGAuthenticationError(PRTGError):
    pass


class ResponseTypes:
    @staticmethod
    def json(data):
        return json.loads(data)

    # @staticmethod
    # def xml(data):
    #     return etree_to_dict(ElementTree.XML(data))


class API:
    def __init__(self, host, username, passhash):
        self._host = host
        self._authparams = {
            "username": username,
            "passhash": passhash
        }

    def _call(self, method, response_type=None, **params):
        if response_type is None:
            response_type = 'json'
        if not hasattr(ResponseTypes, response_type):
            raise ValueError("Unknown response type", response_type)
        url = '%s%s/%s.%s' % (self._host, entrypoint, method, response_type)
        try:
            params = dict(params, **self._authparams)
            response = requests.get(url, params)
            if response.status_code != 200:
                logger.warning("Wrong exit code %d for %s", response.status_code, url)
                raise PRTGError("Invalid HTTP code response", response.status_code)
            return getattr(ResponseTypes, response_type)(response.content.decode('utf-8'))
        except Exception as e:
            raise PRTGError(e) from e

    def __getattr__(self, item):
        return functools.partial(self._call, item)

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

