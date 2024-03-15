import pytest


@pytest.fixture(scope="function")
def channel_id():
    return "1234567890"
