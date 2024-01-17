import logging
from bisect import insort  # adds to a list in sorted order
from dataclasses import dataclass, field

from databases import Database

from app.errors import NotFoundError
from app.models import database

# TODO transactions
log = logging.getLogger(__name__)


@dataclass(frozen=True, order=True)
class Participant:
    name: str = field(compare=False)
    initiative: int
    tiebreaker: int | None = None

    def __str__(self):
        if self.tiebreaker is None:
            return f"{self.initiative}: {self.name}"
        else:
            return f"{self.initiative} ({self.tiebreaker}): {self.name}"

    def as_dict(self):
        return {self.initiative: self.name}


@dataclass(frozen=True)
class InitiativeTracker:
    id: int
    channel_id: str | int
    current_round: int
    participants: tuple[Participant] = field(default_factory=tuple)  # type: ignore

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


async def create_initiative(
    channel_id: str | int, current_round: int = 1, database: Database = database
):
    """Creates an initiative tracker."""
    await database.execute(
        "INSERT INTO initiative_trackers (channel_id, current_round) VALUES (:channel_id, :current_round)",
        {"channel_id": str(channel_id), "current_round": current_round},
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
            name=p._mapping["player_name"],
            initiative=p["init_value"],
            tiebreaker=p["tiebreaker"],
        )
        for p in db_participants
    ]
    return InitiativeTracker(
        id=db_init["id"],
        channel_id=db_init["channel_id"],
        current_round=db_init["current_round"],
        participants=tuple(final_participants),  # type: ignore
    )


async def add_participant(
    channel_id: str | int,
    player_name: str,
    initiative: int,
    database: Database = database,
) -> InitiativeTracker:
    """Adds a character to an initiative tracker."""
    log.info("Adding participant...")
    tracker = await get_initiative(channel_id, database=database)

    await database.execute(
        "INSERT INTO initiative_members (initiative_id, player_name, init_value) VALUES (:initiative_id, :player_name, :init_value)",
        {
            "initiative_id": tracker.id,
            "player_name": player_name,
            "init_value": initiative,
        },
    )
    log.info("Participant added!")

    new_participant = Participant(name=player_name, initiative=initiative)
    new_participants = tracker.participants + (new_participant,)
    new_tracker = InitiativeTracker(
        id=tracker.id,
        channel_id=tracker.channel_id,
        current_round=tracker.current_round,
        participants=new_participants,  # type: ignore
    )
    return new_tracker


async def remove_participant(
    channel_id: str | int, player_name: str, database: Database = database
) -> InitiativeTracker:
    """Removes a character from an initiative tracker."""
    pass


async def update_participant(
    channel_id: str | int,
    player_name: str,
    initiative: int,
    database: Database = database,
) -> InitiativeTracker:
    """Updates a character in an initiative tracker."""
    tracker = await get_initiative(channel_id, database=database)

    await database.execute(
        "UPDATE initiative_members SET init_value = :init_value, player_name = :player_name WHERE initiative_id = :initiative_id",
        {
            "initiative_id": tracker.id,
            "player_name": player_name,
            "init_value": initiative,
        },
    )

    updated_participant = Participant(name=player_name, initiative=initiative)
    updated_participants = tuple(
        p if p.name != player_name else updated_participant for p in tracker.participants
    )
    updated_tracker = InitiativeTracker(
        id=tracker.id,
        channel_id=tracker.channel_id,
        current_round=tracker.current_round,
        participants=updated_participants,  # type: ignore
    )
    return updated_tracker


async def delete_initiative(channel_id: str | int, database: Database = database):
    """Deletes an initiative tracker."""
    pass
