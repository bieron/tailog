import os
from string import ascii_letters
from app.routes import OUTPUT_FORMATS

APP_LOG_DIR = os.environ['LOG_DIR']

def _write_expects(expects, filename):
    with open(f'{APP_LOG_DIR}/{filename}', 'w') as f:
        f.write('\n'.join(expects))
        f.write('\n')


def test_api(client):
    r = client.get('/rest/files/400?n=bad')
    assert r.status_code == 400, r.data
    assert r.get_json()['error'] == "'n' param expects int, not 'bad'"

    _write_expects([], '400')

    r = client.get('/rest/files/400?format=bad')
    assert r.status_code == 400, r.data
    assert r.get_json()['error'] == \
            f"'format' must be one of {OUTPUT_FORMATS}, not 'bad'"

    r = client.get('/rest/files/404')
    assert r.status_code == 404, r.data
    assert 'does not exist' in r.get_json()['error']

    r = client.get('/rest/files/404?delegate=')
    assert r.status_code == 400, r.data
    error = r.get_json()['error']
    assert "'delegate' param invalid: list cannot be empty" in error

    r = client.get('/rest/files/404?delegate=foo,,bar')
    assert r.status_code == 400, r.data
    error = r.get_json()['error']
    assert "'delegate' param invalid: addresses cannot be empty" in error

    for fmt in OUTPUT_FORMATS:
        r = client.get(f'/rest/files/?format={fmt}')
        assert r.status_code == 200, r.data
        r = client.get(f'/rest/files/400?format={fmt}')
        assert r.status_code == 200, r.data



def test_rest(client):
    r = client.get('/rest/files/')
    assert r.status_code == 200, r.data
    resp = r.get_json()
    assert 'objects' in resp
    assert type(resp['objects']) is list
    assert not len(resp['objects'])

    expects = ascii_letters
    filename = 'test_rest'

    _write_expects(expects, filename)

    r = client.get('/rest/files/')
    paths = r.get_json()['objects']
    assert len(paths) == 1
    assert paths[0].keys() == {'path', 'url'}, paths[0]
    assert paths[0]['path'] == filename
    url = paths[0]['url']

    r = client.get(url)
    assert r.status_code == 200, r.data
    resp = r.get_json()
    assert 'objects' in resp

    reversed_expects = list(reversed(expects))

    default_limit = 10

    assert resp['objects'] == reversed_expects[:default_limit]

    limit = 1

    r = client.get(f'{url}?n={limit}&trim=0')
    lines = r.get_json()['objects']
    assert len(lines) == limit
    assert lines[0] == reversed_expects[0] + '\n'


def test_match(client):
    expects = [
        'not matching',
        'foo bar.baz',
        'nope',
        'bazinga',
        'baz',
        'BAZ',
    ]
    filename = 'test_match'

    _write_expects(expects, filename)
    r = client.get(f'/rest/files/{filename}')
    resp = r.get_json()
    assert len(resp['objects']) == len(expects)

    needle = 'baz'

    r = client.get(f'/rest/files/{filename}?match={needle}')
    lines = r.get_json()['objects']
    reversed_expects = [l for l in reversed(expects) if needle in l]
    assert len(reversed_expects) == 3 # sanity check
    assert lines == reversed_expects


    limit = 2
    r = client.get(f'/rest/files/{filename}?match={needle}&n={limit}')
    lines = r.get_json()['objects']
    assert lines == reversed_expects[:limit]


def test_border_cases(client):

    def _mkfile(path):
        with open(f'{APP_LOG_DIR}/{path}', 'w'):
            pass

    filename = 'forbidden'
    _mkfile(filename)
    os.chmod(f'{APP_LOG_DIR}/{filename}', 0o000)
    r = client.get(f'/rest/files/{filename}')
    assert r.status_code == 403
    assert r.get_json()['error'].startswith(
        'You do not have permissions to read')

    filename = 'empty'
    _mkfile(filename)
    r = client.get(f'/rest/files/{filename}')
    assert r.status_code == 200
    assert r.get_json()['objects'] == []


def test_jailbreak(client):
    r = client.get(f'/rest/files/../../etc/passwd')
    assert r.status_code == 403
    error = r.get_json()
    assert error.keys() == {'error'}
    assert error['error'].startswith('/etc/passwd lies outside of ')

    r = client.get(f'/rest/files/~/.bashrc')
    assert r.status_code == 404
    assert 'does not exist' in r.get_json()['error']


def test_bad_file(client):
    filename = 'binary'
    with open(f'{APP_LOG_DIR}/{filename}', 'wb') as f:
        f.write(b'\x00\xaf')

    r = client.get(f'/rest/files/{filename}')
    assert r.status_code == 406
    expected = f"'{APP_LOG_DIR}/{filename}' is unreadable, probably binary"
    assert r.get_json()['error'] == expected


def test_dir_recurse(client):
    os.mkdir(os.path.join(APP_LOG_DIR, 'dir'))
    path = 'dir/file'
    expects = ['anything']
    _write_expects(expects, path)
    r = client.get(f'/rest/files/')
    assert r.status_code == 200
    files = r.get_json()['objects']
    assert files
    for f in files:
        if f['path'] == path:
            url = f['url']
            break
    else:
        assert False, f"'{path}' not found in {files}"

    r = client.get(url)
    assert r.status_code == 200
    assert r.get_json()['objects'] == expects
