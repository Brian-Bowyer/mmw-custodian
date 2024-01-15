import pytest
import pytest_asyncio
from databases import Database

from app.constants import DATABASE_URL
from app.models import Base, database, engine


@pytest.fixture(scope="session", autouse=True)
def recreate_database():
    """Recreates the database."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
