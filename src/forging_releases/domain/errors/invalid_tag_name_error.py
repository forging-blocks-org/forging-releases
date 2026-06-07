"""Error types for invalid Git tag names.

Provides ``InvalidTagNameError`` raised when a tag name does not match the
expected ``v<version>`` format.
"""

from forging_blocks.foundation import ErrorMessage, ValidationError


class InvalidTagNameError(ValidationError):
    """Raised when a tag name does not follow the ``v<version>`` convention."""

    def __init__(self, value: str) -> None:
        """Initialize the error.

        Args:
            value: The invalid tag name that was provided.
        """
        super().__init__(
            ErrorMessage(f"Invalid tag name '{value}'. Tags must start with 'v<version>'.")
        )
