"""Error raised when a release level string is not valid."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class InvalidReleaseLevelValueError(RuleViolationError):
    """Raised when the provided release level is not major, minor, or patch."""

    def __init__(self, level: str) -> None:
        message = ErrorMessage(
            f"Invalid release level: '{level}'. Expected 'major', 'minor', or 'patch'."
        )
        super().__init__(message)
