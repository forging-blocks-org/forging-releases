"""Error types for invalid release versions.

Provides ``InvalidReleaseVersionError`` raised when a version string does not
match the ``<major>.<minor>.<patch>`` format with non-negative integers.
"""

from forging_blocks.foundation import ErrorMessage, ErrorMetadata, ValidationError


class InvalidReleaseVersionError(ValidationError):
    """Raised when a version string is not a valid ``major.minor.patch`` triplet."""

    def __init__(self, release_version: str) -> None:
        """Initialize the error.

        Args:
            release_version: The invalid version string that was provided.
        """
        message = ErrorMessage(
            f"Invalid release version '{release_version}'. Expected '<major>.<minor>.<patch>'"
            " with non-negative integers."
        )

        metadata = ErrorMetadata(context={"release_version": release_version})
        super().__init__(message, metadata)
