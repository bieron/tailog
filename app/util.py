def error_response(ex, code=400):
    return {'error': str(ex)}, code


def for_presentation(path, base):
    return {
        'path': path,
        'url': f'{base}{path}',
    }


def boolean(v):
    return v.lower() not in ('false', 'f', 'no', 'n', '0')


def validate_input(args, **schema):
    params = {}
    for key, meta in schema.items():
        default = meta['default']
        call = meta['type']

        try:
            val = args[key]
        except KeyError:
            params[key] = default
            continue

        try:
            val = call(val)
        except ValueError:
            raise ValueError(
                f"'{key}' param expects {call.__name__}, not '{val}'"
            )

        try:
            values = meta['values']
            if val not in values:
                raise ValueError(
                    f"'{key}' must be one of {values}, not '{val}'"
                )
        except KeyError:
            pass

        params[key] = val
    return params
