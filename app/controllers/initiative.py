import logging

from databases import Database

from app.models import database

# TODO transactions
log = logging.getLogger(__name__)


async def create_initiative(
    channel_id: str | int,
    current_round: int = 1,
    database: Database = database,
):
    """Creates an initiative tracker."""
    log.info("Creating initiative tracker...")
    await database.execute(
        "INSERT INTO initiative_trackers (channel_id, current_round) VALUES (:channel_id, :current_round)",
        {"channel_id": str(channel_id), "current_round": current_round},
    )
    log.info("Initiative tracker created!")


async def delete_initiative(tracker_id: str | int):
    """Deletes an initiative tracker."""
    pass


async def get_initiative(channel_id: str | int | None, tracker_id: str | int | None):
    """Gets an initiative tracker."""
    pass


async def add_to_initiative(tracker_id: str | int, player_name: str, initiative: int):
    """Adds a character to an initiative tracker."""
    pass


async def remove_from_initiative(tracker_id: str | int, player_name: str):
    """Removes a character from an initiative tracker."""
    pass


async def update_initiative(tracker_id: str | int, player_name: str, initiative: int):
    """Updates an initiative tracker."""
    pass
