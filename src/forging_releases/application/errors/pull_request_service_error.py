"""Errors raised by the configured pull-request adapter."""

from forging_blocks.foundation.errors import Error, ErrorMessage, RuntimeErrorMixin


class PullRequestServiceError(RuntimeErrorMixin, Error[dict[str, object]]):
    """Describe a pull-request operation failure using adapter-owned text."""

    def __init__(self, operation: str, message: str) -> None:
        """Initialize the failed operation and its actionable message."""
        self.operation = operation
        super().__init__(ErrorMessage(message))
