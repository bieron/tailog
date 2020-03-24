import pytest
import os
import sys
from tempfile import mkdtemp
from shutil import rmtree

sys.path += ['.', 'venv/lib/python3.8/site-packages']

def pytest_configure():
    os.environ['LOG_DIR'] = mkdtemp()


def pytest_unconfigure():
    try:
        rmtree(os.environ['LOG_DIR'])
    except OSError:
        pass


@pytest.fixture
def app():
    from app import app as myapp
    return myapp
