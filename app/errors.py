class NotFoundError(Exception):
    """An error that is raised when an object cannot be found in the database."""


class AlreadyExistsError(Exception):
    """An error that is raised when an object already exists in the database."""


class BacktrackError(ValueError):
    """An error that is raised when a value is attempted to be reduced below its min value."""
