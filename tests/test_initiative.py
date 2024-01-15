import pytest
from databases import Database

from app.constants import DATABASE_URL
from app.controllers import initiative


@pytest.mark.asyncio
async def test_it_creates_an_initiative():
    # assert db.url == database.url
    async with Database(DATABASE_URL) as db:
        await initiative.create_initiative("123456", database=db)
        db_entry = await db.fetch_one(
            "SELECT * FROM initiative_trackers WHERE channel_id = '123456'"
        )
        assert db_entry is not None
        assert db_entry["channel_id"] == "123456"
