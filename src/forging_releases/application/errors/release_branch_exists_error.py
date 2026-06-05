"""Error returned when a release branch already exists with the same changes."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class ReleaseBranchExistsError(RuleViolationError):
    """Represents an attempt to create a release branch that already exists with no new changes."""

    def __init__(self, branch_name: str) -> None:
        self.branch_name = branch_name
        message = ErrorMessage(
            f"Release branch '{branch_name}' already exists with the same changes"
        )
        super().__init__(message)
