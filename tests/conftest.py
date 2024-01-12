import pytest
import pytest_asyncio
from databases import Database
from sqlalchemy_utils import create_database, drop_database

from app.constants import DATABASE_URL
from app.tables.base import Base, database, engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db() -> Database:
    """Returns a database object."""
    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture(scope="session", autouse=True)
def recreate_database():
    """Recreates the database."""
    # just in case the last test run failed to drop
    try:
        drop_database(engine.url)
    except:
        pass

    create_database(engine.url)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    drop_database(engine.url)
