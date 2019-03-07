import os
from flask import jsonify, Response
import flask


class FileResponse(Response):
    default_mimetype = 'application/octet-stream'

    def __init__(self, filename, **kwargs):
        if not os.path.isabs(filename):

            filename = os.path.join(flask.current_app.root_path, filename)

        with open(filename, 'rb') as f:
            contents = f.read()

        response = contents
        super().__init__(response, **kwargs)


class StatusResponse(FileResponse):
    default_mimetype = 'image/png'

    def __init__(self, status, **kwargs):
        if status is True:
            status = 'ok'
        elif status is False:
            status = 'nok'
        else:
            status = 'unk'

        filename = 'static/status-%s.png' % (status,)
        super().__init__(filename, **kwargs)


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
    def status(status_):
        return StatusResponse(status_)
