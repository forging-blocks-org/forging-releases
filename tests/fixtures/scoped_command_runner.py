from __future__ import annotations

import logging
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from forging_releases.application.errors import CommandExecutionError
from forging_releases.application.ports.outbound import CommandRunner

# When running inside a git hook (e.g. pre-push via pre-commit), GIT_DIR and
# related env vars point at the main repository. These leak into test fixtures
# that create ephemeral git repos in temp directories and break git operations.
# We remove them from the subprocess environment so that git uses the cwd-based
# repo discovery instead.
SANITIZED_ENV = {
    k: v
    for k, v in os.environ.items()
    if k
    not in {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    }
}


class ScopedCommandRunner(CommandRunner):
    """Command runner that executes commands in a specific directory."""

    def __init__(self, working_directory: Path):
        self._cwd = working_directory

    def run(
        self,
        command: Sequence[str],
        *,
        check: bool = True,
    ) -> str:
        """Run a command in the specified working directory."""
        logging.debug("Running command in %s: %s", self._cwd, " ".join(command))

        try:
            result = subprocess.run(
                command,
                cwd=self._cwd,
                check=check,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=SANITIZED_ENV,
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
