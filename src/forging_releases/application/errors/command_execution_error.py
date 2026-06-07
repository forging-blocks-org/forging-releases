"""Error returned when a system command required by the release workflow fails to execute."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class CommandExecutionError(RuleViolationError):
    """Represents a failure to execute a system command required by the release workflow."""

    def __init__(self, command: str, details: str) -> None:
        """Initialize the error.

        Args:
            command: The name of the command that failed.
            details: A description of the failure reason.
        """
        self.command = command
        message = ErrorMessage(f"Command failed: {details} (command: {command})")
        super().__init__(message)
