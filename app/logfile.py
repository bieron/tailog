import magic
import os
from glob import glob
from logging import getLogger

def __get_log_dir():
    try:
        log_dir = os.environ['LOG_DIR']
    except KeyError:
        return '/var/log'

    log_dir = log_dir.rstrip('/')
    try:
        os.listdir(log_dir)
    except OSError as e:
        log.error('Invalid LOG_DIR environment variable. Error: %s', e)
    return log_dir

LOG_DIR = __get_log_dir()
OFFSET = len(LOG_DIR) + 1
GLOB = f'{LOG_DIR}/**'

log = getLogger(__name__)


def is_text_file(f):
    return os.path.isfile(f) and magic.from_file(f, mime=True) == 'text/plain'


def abspath(path):
    path = os.path.abspath(f'{LOG_DIR}/{path}')
    if not path.startswith(f'{LOG_DIR}/'):
        raise ValueError(f'{path} lies outside of {LOG_DIR}')
    return path


def get_all():
    paths = []
    for f in glob(GLOB, recursive=True):
        try:
            if is_text_file(f):
                paths.append(f[OFFSET:])
        except PermissionError:
            log.warning('Skipping denied file %s', f)
    return sorted(paths)


def tail(path, count=10, match=None):
    if match:
        # simple stringsearch
        # TODO globbing, regexes
        sieve = lambda lines: [l for l in lines if match in l]
    else:
        sieve = lambda lines: lines

    with open(path) as f:
        if count < 0:
            return sieve(f.readlines())

        matches = []
        block_size = 4096

        # read file from the end in incrementally larger blocks
        i = -1

        while len(matches) < count:
            try:
                f.seek(i * block_size, os.SEEK_END)
            except IOError:
                # file too small, just read it all
                f.seek(0)
                matches = sieve(f.readlines())
                break

            matches = sieve(f.readlines())
            i -= 1

    return matches[-count:]
