import logging
from bisect import insort  # adds to a list in sorted order
from dataclasses import dataclass, field

from databases import Database

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
    log.info("Creating initiative tracker...")
    await database.execute(
        "INSERT INTO initiative_trackers (channel_id, current_round) VALUES (:channel_id, :current_round)",
        {"channel_id": str(channel_id), "current_round": current_round},
    )
    log.info("Initiative tracker created!")


async def get_initiative(channel_id: str | int, database: Database = database):
    """Gets an initiative tracker."""
    query = "SELECT * FROM initiative_trackers WHERE channel_id = :channel_id"
    # TODO this returns a db object, convert it to something nicer
    return await database.fetch_one(query, {"channel_id": str(channel_id)})


async def add_participant(
    channel_id: str | int,
    player_name: str,
    initiative: int,
    database: Database = database,
):
    """Adds a character to an initiative tracker."""
    pass


async def remove_participant(
    channel_id: str | int, player_name: str, database: Database = database
):
    """Removes a character from an initiative tracker."""
    pass


async def update_participant(
    channel_id: str | int,
    player_name: str,
    initiative: int,
    database: Database = database,
):
    """Updates a participant in an initiative tracker."""
    pass


async def delete_initiative(channel_id: str | int, database: Database = database):
    """Deletes an initiative tracker."""
    pass
