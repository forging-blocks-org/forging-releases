import logging
import subprocess
from collections.abc import Sequence

from forging_releases.application.errors import CommandExecutionError
from forging_releases.application.ports.outbound import CommandRunner


class SubprocessCommandRunner(CommandRunner):
    """Execute commands through :mod:`subprocess`."""

    def run(self, command: Sequence[str], *, check: bool = True) -> str:
        """Run a command and return its unmodified standard output.

        ``check=False`` returns output for non-zero exits. When checking is
        enabled, process streams and the actual return code are preserved in
        :class:`CommandExecutionError` for provider adapters to interpret.
        """
        logging.debug("Running command: %s", " ".join(command))
        try:
            result = subprocess.run(
                command,
                check=check,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            raise CommandExecutionError(
                tuple(command),
                exc.returncode,
                stdout,
                stderr,
            ) from exc
        return result.stdout
