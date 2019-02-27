from argparse import ArgumentParser
from viaastatus.server import wsgi
import logging


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
    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level')

    return parser


def main():
    args = argparser().parse_args()
    logging.basicConfig(level=args.log_level.upper())
    logging.getLogger().setLevel(args.log_level.upper())
    del args.log_level
    wsgi.create_app().run(**args)


if __name__ == '__main__':
    main()
