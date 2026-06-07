"""Error returned when a version string cannot be parsed into a valid release version."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class InvalidVersionError(RuleViolationError):
    """Represents an invalid version string that cannot be parsed as semver."""

    def __init__(self, version: str) -> None:
        """Initialize the error.

        Args:
            version: The invalid version string provided.
        """
        message = ErrorMessage(f"Invalid version format: '{version}'. Expected major.minor.patch.")
        super().__init__(message)
