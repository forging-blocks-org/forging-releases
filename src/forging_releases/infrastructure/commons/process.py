import logging
import subprocess
from abc import ABC, abstractmethod

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)


class CommandRunner(ABC):
    """Abstraction for running system commands."""

    @abstractmethod
    def run(
        self,
        cmd: list[str],
        *,
        check: bool = True,
        suppress_error_log: bool = False,
    ) -> str:
        """Run a shell command and return its output.

        Args:
            cmd: The command and its arguments as a list of strings.
            check: Whether to raise an error on non-zero exit codes.

        Returns:
            The standard output of the command as a string.

        Raises:
            RuntimeError: If the command fails and check is True.
        """
        pass


class SubprocessCommandRunner(CommandRunner):
    def run(
        self,
        cmd: list[str],
        *,
        check: bool = True,
        suppress_error_log: bool = False,
    ) -> str:
        """Run a command and return stdout.

        Raises RuntimeError on failure.
        """
        logging.debug(f"Running command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=check,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            log_level = self._resolve_log_level(suppress_error_log)
            error_msg = self._format_error_message(cmd, exc)
            logging.log(log_level, error_msg)
            raise RuntimeError(error_msg) from exc

    @staticmethod
    def _resolve_log_level(suppress_error_log: bool) -> int:
        """Return DEBUG for expected failures, ERROR for unexpected ones."""
        return logging.DEBUG if suppress_error_log else logging.ERROR

    def _format_error_message(
        self, cmd: list[str], exc: subprocess.CalledProcessError
    ) -> str:
        """Build a user-friendly error message from a command failure."""
        stderr_output = exc.stderr.strip() if exc.stderr else ""
        error_context = self._resolve_error_context(cmd, stderr_output, exc.returncode)
        error_msg = f"Command failed: {' '.join(cmd)}"
        if error_context:
            error_msg += f"\n{error_context}"
        return error_msg

    def _resolve_error_context(
        self, cmd: list[str], stderr: str, returncode: int
    ) -> str:
        """Return human-readable context for a command failure.

        Git commands get tailored messages via ``_get_git_error_context``;
        non-git commands show raw stderr or the exit code as a fallback.
        """
        if cmd[0] == "git":
            return self._get_git_error_context(cmd, stderr)
        return stderr or f"Command exited with code {returncode}"

    def _get_git_error_context(self, cmd: list[str], stderr: str) -> str:
        if "commit" in cmd and "nothing to commit" in stderr:
            return "Nothing to commit - working tree clean"
        elif "commit" in cmd and stderr:
            return f"Commit failed: {stderr}"
        elif "push" in cmd and "rejected" in stderr:
            return f"Push rejected: {stderr}"
        elif "push" in cmd and stderr:
            return f"Push failed: {stderr}"
        elif stderr:
            return stderr
        else:
            return f"Git command failed with exit code {cmd}"
