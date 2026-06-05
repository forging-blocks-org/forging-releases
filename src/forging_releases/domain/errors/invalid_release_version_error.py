from forging_blocks.foundation import ErrorMessage, ErrorMetadata, ValidationError


class InvalidReleaseVersionError(ValidationError):
    def __init__(self, release_version: str) -> None:
        message = ErrorMessage(
            f"Invalid release version '{release_version}'. Expected '<major>.<minor>.<patch>'"
            " with non-negative integers."
        )

        metadata = ErrorMetadata(context={"release_version": release_version})
        super().__init__(message, metadata)
