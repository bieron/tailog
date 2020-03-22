import pytest
import os
from tempfile import mkdtemp
from shutil import rmtree

def pytest_configure():
    os.environ['LOG_DIR'] = mkdtemp()


def pytest_unconfigure():
    try:
        rmtree(os.environ['LOG_DIR'])
    except OSError:
        pass


@pytest.fixture
def app(tmpdir):
    from app import app as myapp
    return myapp
