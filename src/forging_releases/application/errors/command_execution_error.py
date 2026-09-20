"""Structured errors raised when an external command exits unsuccessfully."""

from forging_blocks.foundation.errors import Error, ErrorMessage, RuntimeErrorMixin


class CommandExecutionError(RuntimeErrorMixin, Error[dict[str, object]]):
    """Describe a failed command while preserving all process diagnostics."""

    def __init__(
        self,
        command: tuple[str, ...],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        """Initialize with the command and captured process result streams."""
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        detail = stderr.strip() or stdout.strip() or f"exit code {returncode}"
        super().__init__(
            ErrorMessage(
                f"Command failed with exit code {returncode}: {' '.join(command)}"
                f" ({detail})"
            )
        )
