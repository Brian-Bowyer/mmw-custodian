import logging
from bisect import insort  # adds to a list in sorted order
from dataclasses import dataclass, field

from asyncpg.exceptions import UniqueViolationError
from databases import Database

from app.errors import AlreadyExistsError, NotFoundError
from app.models import database

# TODO transactions
log = logging.getLogger(__name__)


@dataclass(frozen=True, order=True)
class Participant:
    name: str = field(compare=False)
    initiative: int
    tiebreaker: int = 0

    def __str__(self):
        if self.tiebreaker is None:
            return f"{self.initiative}: {self.name}"
        else:
            return f"{self.initiative} ({self.tiebreaker}): {self.name}"

    def as_dict(self):
        return {self.initiative: self.name}

    def is_before(self, other) -> bool:
        return (self.initiative, self.tiebreaker) < (other.initiative, other.tiebreaker)


@dataclass(frozen=True)
class InitiativeTracker:
    id: int
    channel_id: str | int
    current_round: int
    current_index: int
    participants: tuple[Participant, ...] = field(default_factory=tuple)

    def __post_init__(self):
        """Sorts the participants by initiative and tiebreaker."""
        sorted_participants = tuple(sorted(self.participants, reverse=True))

        # need to do this weird assignment method b/c frozen=True
        object.__setattr__(self, "participants", sorted_participants)

    def __str__(self):
        """Returns a string representation of the initiative tracker."""
        if self.participants:
            participant_list = "\n".join(str(p) for p in self.participants)
        else:
            participant_list = "Nobody!\n"

        return f"Round {self.current_round}\n" + f"Participants:\n" + participant_list

    def as_dict(self):
        return {p.name: p.initiative for p in self.participants}

    def find_participant(self, name: str) -> Participant | None:
        """Finds a participant by name."""
        for participant in self.participants:
            if participant.name == name:
                return participant
        return None

    @property
    def current_participant(self) -> Participant:
        """Returns the current participant."""
        return self.participants[self.current_index]


async def create_initiative(
    channel_id: str | int,
    current_round: int = 1,
    current_index=0,
    database: Database = database,
) -> InitiativeTracker:
    """Creates an initiative tracker."""
    try:
        await database.execute(
            "INSERT INTO initiative_trackers (channel_id, current_round, current_index) VALUES (:channel_id, :current_round, :current_index)",
            {
                "channel_id": str(channel_id),
                "current_round": current_round,
                "current_index": current_index,
            },
        )
    except UniqueViolationError:
        raise AlreadyExistsError(
            f"Initiative tracker for channel {channel_id} already exists!"
        )

    return await get_initiative(channel_id, database=database)


async def get_initiative(
    channel_id: str | int, database: Database = database
) -> InitiativeTracker:
    """Gets an initiative tracker."""
    query = "SELECT * FROM initiative_trackers WHERE channel_id = :channel_id"
    db_init = await database.fetch_one(query, {"channel_id": str(channel_id)})
    if db_init is None:
        raise NotFoundError(f"Initiative tracker for channel {channel_id} not found!")

    db_participants = await database.fetch_all(
        "SELECT * FROM initiative_members WHERE initiative_id = :initiative_id",
        {"initiative_id": db_init["id"]},
    )
    final_participants = [
        Participant(
            name=p["player_name"],
            initiative=p["init_value"],
            tiebreaker=p["tiebreaker"],
        )
        for p in db_participants
    ]
    return InitiativeTracker(
        id=db_init["id"],
        channel_id=db_init["channel_id"],
        current_round=db_init["current_round"],
        current_index=db_init["current_index"],
        participants=tuple(final_participants),
    )


async def delete_initiative(channel_id: str | int, database: Database = database):
    """Deletes an initiative tracker."""
    await database.execute(
        "DELETE FROM initiative_trackers WHERE channel_id = :channel_id",
        {"channel_id": str(channel_id)},
    )


async def add_participant(
    channel_id: str | int,
    player_name: str,
    initiative: int,
    tiebreaker: int = 0,
    database: Database = database,
) -> InitiativeTracker:
    """Adds a character to an initiative tracker."""
    tracker = await get_initiative(channel_id, database=database)

    try:
        await database.execute(
            "INSERT INTO initiative_members (initiative_id, player_name, init_value, tiebreaker) VALUES (:initiative_id, :player_name, :init_value, :tiebreaker)",
            {
                "initiative_id": tracker.id,
                "player_name": player_name,
                "init_value": initiative,
                "tiebreaker": tiebreaker,
            },
        )
    except UniqueViolationError:
        raise AlreadyExistsError(
            f"Participant {player_name} already exists in this initiative!"
        )

    new_participant = Participant(
        name=player_name, initiative=initiative, tiebreaker=tiebreaker
    )
    new_participants = tracker.participants + (new_participant,)
    new_tracker = InitiativeTracker(
        id=tracker.id,
        channel_id=tracker.channel_id,
        current_round=tracker.current_round,
        current_index=tracker.current_index,
        participants=new_participants,
    )
    return new_tracker


async def remove_participant(
    channel_id: str | int, player_name: str, database: Database = database
) -> InitiativeTracker:
    """Removes a character from an initiative tracker."""
    tracker = await get_initiative(channel_id, database=database)

    await database.execute(
        "DELETE FROM initiative_members WHERE initiative_id = :initiative_id AND player_name = :player_name",
        {"initiative_id": tracker.id, "player_name": player_name},
    )

    new_participants = tuple(p for p in tracker.participants if p.name != player_name)
    new_tracker = InitiativeTracker(
        id=tracker.id,
        channel_id=tracker.channel_id,
        current_round=tracker.current_round,
        current_index=tracker.current_index,
        participants=new_participants,
    )

    return new_tracker


async def update_participant(
    channel_id: str | int,
    player_name: str,
    initiative: int,
    tiebreaker: int = 0,
    database: Database = database,
) -> InitiativeTracker:
    """Updates a character in an initiative tracker."""
    tracker = await get_initiative(channel_id, database=database)

    await database.execute(
        "UPDATE initiative_members SET init_value = :init_value, tiebreaker = :tiebreaker WHERE initiative_id = :initiative_id AND player_name = :player_name",
        {
            "initiative_id": tracker.id,
            "player_name": player_name,
            "init_value": initiative,
            "tiebreaker": tiebreaker,
        },
    )

    updated_participant = Participant(
        name=player_name, initiative=initiative, tiebreaker=tiebreaker
    )
    updated_participants = tuple(
        p if p.name != player_name else updated_participant for p in tracker.participants
    )
    updated_tracker = InitiativeTracker(
        id=tracker.id,
        channel_id=tracker.channel_id,
        current_round=tracker.current_round,
        current_index=tracker.current_index,
        participants=updated_participants,
    )
    return updated_tracker


async def next_participant(
    channel_id: str | int,
    database: Database = database,
) -> InitiativeTracker:
    """Moves to the next participant in an initiative tracker."""
    tracker = await get_initiative(channel_id, database=database)

    return tracker


async def previous_participant():
    """Moves to the previous participant in an initiative tracker."""
    pass


async def goto_participant():
    """Moves to a specific participant in an initiative tracker."""
    pass
