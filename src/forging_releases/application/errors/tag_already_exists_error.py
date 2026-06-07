"""Error returned when a release tag already exists and cannot be recreated."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class TagAlreadyExistsError(RuleViolationError):
    """Represents an attempt to create a release tag that already exists."""

    def __init__(self, tag_name: str) -> None:
        """Initialize the error.

        Args:
            tag_name: The name of the tag that already exists.
        """
        message = ErrorMessage(f"Tag '{tag_name}' already exists.")
        super().__init__(message)
