import pytest
from databases import Database

from app.constants import DATABASE_URL
from app.controllers import initiative
from app.errors import AlreadyExistsError, BacktrackError, NotFoundError


# NOTE: doing the inefficient thing and creating a new Database object for each test
# b/c asyncpg's event loop is created when the Database object is, and so would
# cause an event loop conflict with pytest_asyncio's every-function loops otherwise
@pytest.mark.asyncio
async def test_create_initiative_creates_an_initiative(channel_id):
    # assert db.url == database.url
    async with Database(DATABASE_URL, force_rollback=True) as db:
        tracker = await initiative.create_initiative(channel_id, database=db)
        db_entry = await db.fetch_one(
            f"SELECT * FROM initiative_trackers WHERE channel_id = '{channel_id}'"
        )
        assert db_entry is not None
        assert db_entry["channel_id"] == channel_id

        assert tracker.id == db_entry["id"]
        assert tracker.channel_id == db_entry["channel_id"]
        assert tracker.current_round == db_entry["current_round"]


@pytest.mark.asyncio
async def test_create_initiative_errors_if_already_exists(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        with pytest.raises(AlreadyExistsError):
            await initiative.create_initiative(channel_id, database=db)


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_initiative_gets_an_initiative(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.get_initiative(channel_id, database=db)
        assert tracker is not None
        assert tracker.channel_id == channel_id


@pytest.mark.asyncio
async def test_get_initiative_errors_if_no_initiative(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        with pytest.raises(NotFoundError):
            _ = await initiative.get_initiative(channel_id, database=db)


@pytest.mark.asyncio
async def test_delete_initiative_deletes_an_initiative(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        db_entry = await db.fetch_one(
            f"SELECT * FROM initiative_trackers WHERE channel_id = '{channel_id}'"
        )
        assert db_entry is not None

        await initiative.delete_initiative(channel_id, database=db)
        db_entry = await db.fetch_one(
            f"SELECT * FROM initiative_trackers WHERE channel_id = '{channel_id}'"
        )
        assert db_entry is None


@pytest.mark.asyncio
async def test_add_participant_adds_a_participant(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        tracker = await initiative.add_participant(
            channel_id, "Alice", 15, tiebreaker=1, database=db
        )
        assert tracker.participants == (
            initiative.Participant("Alice", 15, tiebreaker=1),
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
        assert db_entry[1]["tiebreaker"] == 1


@pytest.mark.asyncio
async def test_add_participant_errors_on_duplicate(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        with pytest.raises(AlreadyExistsError):
            await initiative.add_participant(channel_id, "Bob", 10, database=db)


@pytest.mark.asyncio
async def test_participant_order_is_correct(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )
        tracker = await initiative.add_participant(
            channel_id, "Deborah", 15, tiebreaker=99, database=db
        )
        tracker = await initiative.add_participant(
            channel_id, "Eve", 15, tiebreaker=-10, database=db
        )
        tracker = await initiative.add_participant(channel_id, "Frank", 15, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Aabria", 15, database=db
        )

        # RULES
        # 1. Sort by initiative value, descending
        # 2. Sort by tiebreaker, descending (no tiebreaker = 0)
        # 3. Failing that, recent entires go last
        assert tracker.participants == (
            initiative.Participant("Deborah", 15, tiebreaker=99),
            initiative.Participant("Alice", 15),
            initiative.Participant("Frank", 15),
            initiative.Participant("Aabria", 15),
            initiative.Participant("Eve", 15, tiebreaker=-10),
            initiative.Participant("Bob", 10),
            initiative.Participant("Charlie", 5),
        )


@pytest.mark.asyncio
async def test_remove_participant_removes_a_participant(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)

        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        await initiative.remove_participant(channel_id, "Bob", database=db)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 0


@pytest.mark.skip(reason="Still thinking of a good way to do this")
@pytest.mark.asyncio
async def test_remove_participant_errors_if_not_present(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        with pytest.raises(NotFoundError):
            await initiative.remove_participant(channel_id, "Bob", database=db)


@pytest.mark.asyncio
async def test_update_participant_updates_an_initiative(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        assert tracker.participants == (initiative.Participant("Bob", 10),)
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 10

        tracker = await initiative.update_participant(
            channel_id, "Bob", 15, tiebreaker=2, database=db
        )
        assert tracker.participants == (
            initiative.Participant("Bob", 15, tiebreaker=2),
        )
        db_entry = await db.fetch_all(
            "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
            {"initiative_id": tracker.id},
        )
        assert len(db_entry) == 1
        assert db_entry[0]["player_name"] == "Bob"
        assert db_entry[0]["init_value"] == 15
        assert db_entry[0]["tiebreaker"] == 2


@pytest.mark.skip(reason="Still thinking of a good way to do this")
@pytest.mark.asyncio
async def test_update_participant_errors_if_not_present(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        with pytest.raises(NotFoundError):
            await initiative.update_participant(channel_id, "Bob", 15, database=db)


@pytest.mark.asyncio
async def test_current_participant_does_not_change_when_participants_are_added(
    channel_id,
):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        assert tracker.current_participant == initiative.Participant("Bob", 10)

        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        assert tracker.current_participant == initiative.Participant("Bob", 10)

        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )
        assert tracker.current_participant == initiative.Participant("Bob", 10)

        tracker = await initiative.add_participant(
            channel_id, "Deborah", 10, database=db
        )
        assert tracker.current_participant == initiative.Participant("Bob", 10)


@pytest.mark.asyncio
async def test_next_participant_goes_to_the_next_participant(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )

        assert tracker.current_participant == initiative.Participant("Alice", 15)
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Bob", 10)
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Charlie", 5)


@pytest.mark.asyncio
async def test_next_participant_goes_to_the_first_participant_when_at_the_end(
    channel_id,
):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )

        tracker = await initiative.next_participant(channel_id, database=db)
        tracker = await initiative.next_participant(channel_id, database=db)
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Alice", 15)


@pytest.mark.asyncio
async def test_previous_participant_goes_to_the_previous_participant(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )

        tracker = await initiative.next_participant(channel_id, database=db)
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Charlie", 5)
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Bob", 10)
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Alice", 15)


@pytest.mark.asyncio
async def test_previous_participant_goes_to_the_last_participant_when_at_the_beginning(
    channel_id,
):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )

        tracker = await initiative.next_participant(channel_id, database=db)
        tracker = await initiative.next_participant(channel_id, database=db)
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Alice", 15)

        tracker = await initiative.previous_participant(channel_id, database=db)
        tracker = await initiative.previous_participant(channel_id, database=db)
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_participant == initiative.Participant("Alice", 15)


@pytest.mark.asyncio
async def test_goto_participant_goes_to_the_specified_participant(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )

        tracker = await initiative.goto_participant(channel_id, "Charlie", database=db)
        assert tracker.current_participant == initiative.Participant("Charlie", 5)


@pytest.mark.asyncio
async def test_goto_participant_errors_if_not_present(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        with pytest.raises(NotFoundError):
            await initiative.goto_participant(channel_id, "Charlie", database=db)


@pytest.mark.asyncio
async def test_next_participant_and_previous_participant_wrap_around(channel_id):
    async with Database(DATABASE_URL, force_rollback=True) as db:
        await initiative.create_initiative(channel_id, database=db)
        tracker = await initiative.add_participant(channel_id, "Alice", 15, database=db)
        tracker = await initiative.add_participant(channel_id, "Bob", 10, database=db)
        tracker = await initiative.add_participant(
            channel_id, "Charlie", 5, database=db
        )

        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_round == 1
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_round == 1

        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_round == 2
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_round == 2
        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_round == 2

        tracker = await initiative.next_participant(channel_id, database=db)
        assert tracker.current_round == 3

        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_round == 2
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_round == 2
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_round == 2

        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_round == 1
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_round == 1
        tracker = await initiative.previous_participant(channel_id, database=db)
        assert tracker.current_round == 1

        with pytest.raises(BacktrackError):
            tracker = await initiative.previous_participant(channel_id, database=db)
