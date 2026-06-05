from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class ChangelogGenerationError(RuleViolationError):
    """Represents a failure during changelog generation."""

    def __init__(self, details: str) -> None:
        message = ErrorMessage(f"Changelog generation failed: {details}")
        super().__init__(message)
