"""Error types for invalid release pull requests.

Provides ``InvalidReleasePullRequestError`` raised when a release pull request
fails domain validation.
"""

from forging_blocks.foundation import ErrorMessage, ValidationError


class InvalidReleasePullRequestError(ValidationError):
    """Raised when a release pull request fails domain validation."""

    def __init__(self, reason: str) -> None:
        """Initialize the error.

        Args:
            reason: A human-readable description of the validation failure.
        """
        super().__init__(ErrorMessage(reason))
