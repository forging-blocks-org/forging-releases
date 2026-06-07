"""Error returned when the project configuration file cannot be read or written."""

from forging_blocks.foundation.errors.core import ErrorMessage
from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError


class ProjectConfigurationError(RuleViolationError):
    """Represents a failure to read or write the project configuration file (pyproject.toml)."""

    def __init__(self, operation: str, path: str, details: str) -> None:
        """Initialize the error.

        Args:
            operation: The I/O operation that failed ('read' or 'write').
            path: The filesystem path of the configuration file.
            details: A description of the failure reason (e.g. file not found, permission denied).
        """
        self.operation = operation
        self.path = path
        msg = f"Project configuration {operation} failed: {details} (path: {path})"
        message = ErrorMessage(msg)
        super().__init__(message)
