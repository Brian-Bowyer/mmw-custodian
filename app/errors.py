class NotFoundError(Exception):
    """An error that is raised when an object cannot be found in the database."""


class AlreadyExistsError(Exception):
    """An error that is raised when an object already exists in the database."""
