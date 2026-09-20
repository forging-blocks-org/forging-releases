from forging_blocks.foundation.errors import ErrorMessage, RuleViolationError


class ChangelogGenerationError(RuleViolationError):
    """Raised when changelog generation fails."""

    def __init__(self, details: str) -> None:
        message = ErrorMessage(f"Changelog generation failed: {details}")
        super().__init__(message)