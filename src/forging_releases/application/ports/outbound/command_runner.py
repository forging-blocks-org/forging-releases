"""Outbound port for executing external commands."""

from abc import abstractmethod
from collections.abc import Sequence

from forging_blocks.foundation.ports import OutboundPort


class CommandRunner(OutboundPort):
    """Execute a command without exposing process implementation details."""

    @abstractmethod
    def run(self, command: Sequence[str], *, check: bool = True) -> str:
        """Run ``command`` and return its standard output.

        Args:
            command: Executable and arguments, in invocation order.
            check: Raise :class:`CommandExecutionError` for non-zero exits when true.

        Returns:
            The command's standard output, including its original whitespace.
        """
        ...
