import pytest
import pytest_asyncio
from databases import Database

from app.constants import DATABASE_URL
from app.models import Base, database, engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db() -> Database:
    """Returns a database object."""
    async with Database(DATABASE_URL) as database:
        print("DB open")
        yield database
        print("DB close")


@pytest.fixture(scope="session", autouse=True)
def recreate_database():
    """Recreates the database."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
