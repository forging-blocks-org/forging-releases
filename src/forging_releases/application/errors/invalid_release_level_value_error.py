"""Error returned when a release level string is not valid."""

from forging_blocks.foundation.errors import RuleViolationError
from forging_blocks.foundation.errors.core import ErrorMessage


class InvalidReleaseLevelValueError(RuleViolationError):
    """Represents an invalid release level that is not major, minor, or patch."""

    def __init__(self, level: str) -> None:
        message = ErrorMessage(
            f"Invalid release level: '{level}'. Expected 'major', 'minor', or 'patch'."
        )
        super().__init__(message)
