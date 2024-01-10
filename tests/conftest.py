import pytest
from databases import Database

from app.constants import DATABASE_URL


@pytest.fixture
async def db() -> Database:
    """Returns a database object."""
    return Database(DATABASE_URL)
