import pytest

import app as yt_app


@pytest.fixture()
def client():
    yt_app.app.config.update(TESTING=True)
    with yt_app.app.test_client() as client:
        yield client
