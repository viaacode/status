from argparse import ArgumentParser
from . import wsgi


def argparser():
    """
    Get the help and arguments specific to this module
    """
    parser = ArgumentParser(prog='status', description='A service that supplies status information about our platforms')

    parser.add_argument('--debug', action='store_true',
                        help='run in debug mode')
    parser.add_argument('--host',
                        help='hostname or ip to serve api')
    parser.add_argument('--port', type=int, default=8080,
                        help='port used by the server')
    return parser


def main():
    args = argparser().parse_args()
    wsgi.create_app().run(**args)


if __name__ == '__main__':
    main()
