from forging_blocks.foundation.errors import RuleViolationError
from forging_blocks.foundation.errors.core import ErrorMessage


class TagAlreadyExistsError(RuleViolationError):
    """Raised when attempting to create a release with an existing tag."""

    def __init__(self, tag_name: str) -> None:
        message = ErrorMessage(f"Tag '{tag_name}' already exists.")
        super().__init__(message)
