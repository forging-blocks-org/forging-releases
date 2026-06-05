"""Error raised when a version string cannot be parsed into a valid release version."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class InvalidVersionError(RuleViolationError):
    """Raised when the provided version string is not a valid semver."""

    def __init__(self, version: str) -> None:
        message = ErrorMessage(f"Invalid version format: '{version}'. Expected major.minor.patch.")
        super().__init__(message)
