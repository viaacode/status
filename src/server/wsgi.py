from flask import Flask
import jsonrpcserver
from flask import Flask, request, Response, render_template


def create_app(entrypoint: str=None):
    app = Flask(__name__)

    if entrypoint is None:
        entrypoint = '/'

    @app.route('/ping')
    def ping():
        return 'pong'

    return app


application = create_app()

