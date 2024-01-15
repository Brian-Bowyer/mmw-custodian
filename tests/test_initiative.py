import pytest
from databases import Database

from app.constants import DATABASE_URL
from app.controllers import initiative


# NOTE: doing the inefficient thing and creating a new Database object for each test
# b/c asyncpg's event loop is created when the Database object is, and so would
# cause an event loop conflict with pytest_asyncio's every-function loops otherwise
@pytest.mark.asyncio
async def test_it_creates_an_initiative():
    # assert db.url == database.url
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        db_entry = await db.fetch_one(
            "SELECT * FROM initiative_trackers WHERE channel_id = '123456'"
        )
        assert db_entry is not None
        assert db_entry["channel_id"] == "123456"
