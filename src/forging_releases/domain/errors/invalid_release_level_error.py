"""Error types for invalid release levels.

Provides ``InvalidReleaseLevelError`` raised when a release level string does
not match one of the allowed values: patch, minor, or major.
"""

from forging_blocks.foundation import ErrorMessage, ValidationError


class InvalidReleaseLevelError(ValidationError):
    """Raised when a release level string is not one of ``patch``, ``minor``, or ``major``."""

    def __init__(self, value: str) -> None:
        """Initialize the error.

        Args:
            value: The invalid release level string that was provided.
        """
        super().__init__(
            ErrorMessage(f"Invalid release level '{value}'. Allowed values: patch, minor, major.")
        )
