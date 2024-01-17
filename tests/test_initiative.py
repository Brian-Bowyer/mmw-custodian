import pytest
from databases import Database

from app.constants import DATABASE_URL
from app.controllers import initiative
from app.errors import AlreadyExistsError, NotFoundError


# NOTE: doing the inefficient thing and creating a new Database object for each test
# b/c asyncpg's event loop is created when the Database object is, and so would
# cause an event loop conflict with pytest_asyncio's every-function loops otherwise
@pytest.mark.asyncio
async def test_create_initiative_creates_an_initiative():
    # assert db.url == database.url
    async with Database(DATABASE_URL, force_rollback=True) as db:
        tracker = await initiative.create_initiative("123456", database=db)
        db_entry = await db.fetch_one(
            "SELECT * FROM initiative_trackers WHERE channel_id = '123456'"
        )
        assert db_entry is not None
        assert db_entry["channel_id"] == "123456"

        assert tracker.id == db_entry["id"]
        assert tracker.channel_id == db_entry["channel_id"]
        assert tracker.current_round == db_entry["current_round"]


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_initiative_gets_an_initiative():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        tracker = await initiative.get_initiative("123456", database=db)
        assert tracker is not None
        assert tracker.channel_id == "123456"


@pytest.mark.asyncio
async def test_get_initiative_errors_if_no_initiative():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        with pytest.raises(NotFoundError):
            _ = await initiative.get_initiative("123456", database=db)


@pytest.mark.asyncio
async def test_delete_initiative_deletes_an_initiative():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        db_entry = await db.fetch_one(
            "SELECT * FROM initiative_trackers WHERE channel_id = '123456'"
        )
        assert db_entry is not None

        await initiative.delete_initiative("123456", database=db)
        db_entry = await db.fetch_one(
            "SELECT * FROM initiative_trackers WHERE channel_id = '123456'"
        )
        assert db_entry is None


@pytest.mark.asyncio
async def test_add_participant_adds_a_participant():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        tracker = await initiative.add_participant("123456", "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        tracker = await initiative.add_participant("123456", "Alice", 15, database=db)
        assert tracker.participants == (
            initiative.Participant("Alice", 15),
            initiative.Participant("Bob", 10),
        )
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 2
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10
        assert db_entry[1]["player_name"] == "Alice"
        assert db_entry[1]["init_value"] == 15


@pytest.mark.asyncio
async def test_add_participant_errors_on_duplicate():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        tracker = await initiative.add_participant("123456", "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        with pytest.raises(AlreadyExistsError):
            await initiative.add_participant("123456", "Bob", 10, database=db)


@pytest.mark.asyncio
async def test_remove_participant_removes_a_participant():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        tracker = await initiative.add_participant("123456", "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)

        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        await initiative.remove_participant("123456", "Bob", database=db)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 0


@pytest.mark.asyncio
async def test_update_participant_updates_an_initiative():
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative("123456", database=db)
        tracker = await initiative.add_participant("123456", "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        tracker = await initiative.update_participant("123456", "Bob", 15, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 15),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 15
