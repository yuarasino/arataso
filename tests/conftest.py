import pytest


@pytest.fixture
def settings():
    from config import settings

    return settings
