"""Error returned when a version string cannot be found or parsed from project configuration."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class VersionNotFoundError(RuleViolationError):
    """Represents a failure to find or parse the version from the project configuration."""

    def __init__(self, details: str) -> None:
        """Initialize the error.

        Args:
            details: A description of why the version could not be found.
        """
        message = ErrorMessage(f"Version not found: {details}")
        super().__init__(message)
