import pytest

from pb.pb import create_app


@pytest.fixture
def app():
    app = create_app()
    return app
