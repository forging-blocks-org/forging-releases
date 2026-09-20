"""Errors raised by the configured version-control adapter."""

from forging_blocks.foundation.errors import Error, ErrorMessage, RuntimeErrorMixin


class VersionControlError(RuntimeErrorMixin, Error[dict[str, object]]):
    """Describe a version-control operation failure using adapter-owned text."""

    def __init__(self, operation: str, message: str) -> None:
        """Initialize the failed operation and its actionable message."""
        self.operation = operation
        super().__init__(ErrorMessage(message))
