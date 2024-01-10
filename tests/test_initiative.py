import pytest

from app.controllers import initiative


@pytest.mark.asyncio
async def test_it_creates_an_initiative(db):
    result = await initiative.create_initiative("123456")
    assert result

    db_entry = await db.fetch_one("SELECT * FROM initiative WHERE channel_id = '123456'")
    assert db_entry["channel_id"] == "123456"
