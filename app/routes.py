from app import app, logfile
from flask import request, redirect
from logging import getLogger
from urllib.parse import urlencode
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

from app.util import (error_response, validate_input, boolean, for_presentation,
    address_list)

log = getLogger(__name__)

DEFAULT_LINES_COUNT = 10
OUTPUT_FORMATS = ('json', 'text')

def gather_delegated(hosts, path, args):
    if not args['match']:
        args.pop('match')
    qs = urlencode(args)

    data = {}

    with FuturesSession() as s:
        future_map = {s.get(f'{h}/rest/files/{path}?{qs}') : h for h in hosts}
        for fut in as_completed(future_map.keys()):
            data[ future_map[fut] ] = fut.result().json()

    return data


def list_response(objects, trim=False):
    try:
        args = validate_input(
            request.args, format={
                'type': str,
                'default': OUTPUT_FORMATS[0],
                'values': OUTPUT_FORMATS,
            },
        )
    except ValueError as e:
        return error_response(e, 400)

    if args['format'] == 'text':
        return ''.join(objects)
    #TODO add XML
    if trim:
        objects = [o.strip('\n') for o in objects]
    return {'objects': objects}


@app.route('/')
def index():
    return redirect('/rest/files/')

@app.route('/rest/files/')
def files():
    base_url = request.base_url
    return list_response(
        [for_presentation(f, base_url) for f in logfile.get_all()]
    )


@app.route('/rest/files/<path:path>')
def file(path):
    try:
        args = validate_input(
            request.args,
            n={'default': DEFAULT_LINES_COUNT, 'type': int},
            match={'default': None, 'type': str},
            trim={'default': True, 'type': boolean},
            delegate={'default': None, 'type': address_list}
        )
    except ValueError as e:
        return error_response(e, 400)

    if args['delegate']:
        delegate = args.pop('delegate')
        return gather_delegated(delegate, path, args)

    try:
        path = logfile.abspath(path)
    except ValueError as e:
        return error_response(e, 403)

    try:
        lines = logfile.tail(path, args['n'], args['match'])
    except FileNotFoundError:
        return error_response(f"File '{path}' does not exist", 404)
    except PermissionError:
        return error_response(
            f"You do not have permissions to read '{path}'", 403
        )

    lines.reverse()
    return list_response(lines, args['trim'])
