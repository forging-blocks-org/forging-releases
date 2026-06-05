from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class TagAlreadyExistsError(RuleViolationError):
    """Represents an attempt to create a release tag that already exists."""

    def __init__(self, tag_name: str) -> None:
        message = ErrorMessage(f"Tag '{tag_name}' already exists.")
        super().__init__(message)
