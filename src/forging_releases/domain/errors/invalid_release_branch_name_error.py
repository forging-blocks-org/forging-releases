"""Error types for invalid release branch names.

Provides ``InvalidReleaseBranchNameError`` raised when a branch name does not
match the expected ``release/v<version>`` format.
"""

from forging_blocks.foundation import ErrorMessage, ValidationError


class InvalidReleaseBranchNameError(ValidationError):
    """Raised when a branch name does not follow the ``release/v<version>`` convention."""

    def __init__(self, value: str) -> None:
        """Initialize the error.

        Args:
            value: The invalid branch name that was provided.
        """
        super().__init__(
            ErrorMessage(
                f"Invalid release branch name '{value}'. "
                "Release branches must start with 'release/v<version>'."
            )
        )
