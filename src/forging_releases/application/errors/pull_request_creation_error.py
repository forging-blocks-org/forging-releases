"""Error returned when a pull request cannot be created on the remote repository."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class PullRequestCreationError(RuleViolationError):
    """Represents a failure to create a pull request on the remote repository."""

    def __init__(self, details: str) -> None:
        """Initialize the error.

        Args:
            details: A description of why the pull request creation failed.
        """
        message = ErrorMessage(f"Pull request creation failed: {details}")
        super().__init__(message)
