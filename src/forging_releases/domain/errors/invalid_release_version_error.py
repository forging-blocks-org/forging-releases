from forging_blocks.foundation import ErrorMessage, ErrorMetadata, ValidationError


class InvalidReleaseVersionError(ValidationError):
    def __init__(self, release_version: str) -> None:
<<<<<<< Updated upstream
        message = ErrorMessage(
            f"Invalid release version '{release_version}'. Expected '<major>.<minor>.<patch>'"
            " with non-negative integers."
=======
        message = ErrorMessage(f"'{release_version}' should be bigger than v0.0.0")
        metadata: ErrorMetadata[dict[str, object]] = ErrorMetadata(
            context={"release_version": release_version}
>>>>>>> Stashed changes
        )
        super().__init__(message, metadata)
