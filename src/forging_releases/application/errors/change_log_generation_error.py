"""Error returned when changelog generation fails."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class ChangelogGenerationError(RuleViolationError):
    """Represents a failure during changelog generation."""

    def __init__(self, details: str) -> None:
        """Initialize the error.

        Args:
            details: A description of why changelog generation failed.
        """
        message = ErrorMessage(f"Changelog generation failed: {details}")
        super().__init__(message)
