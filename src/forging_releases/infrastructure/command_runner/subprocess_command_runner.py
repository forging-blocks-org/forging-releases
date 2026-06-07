from __future__ import annotations

import os
import subprocess

from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import CommandExecutionError

"""Subprocess-based command runner with dry-run support."""


class SubprocessCommandRunner:
    """Runs shell commands via subprocess with error extraction and dry-run support."""

    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None) -> None:
        """Initialize the runner.

        Args:
            cwd: Default working directory for commands.
        """
        self._cwd = cwd

    def run(
        self,
        cmd: list[str],
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        dry_run: bool = False,
    ) -> Result[subprocess.CompletedProcess[str], CommandExecutionError]:
        """Execute a command via subprocess.

        Args:
            cmd: The command and arguments as a list of strings.
            cwd: Working directory override. Falls back to the default.
            env: Optional environment variable overrides.
            dry_run: If True, only log the intended command.

        Returns:
            Ok with the CompletedProcess on success,
            Err with CommandExecutionError on failure.
        """
        resolved_cwd = cwd or self._cwd
        resolved_cmd = list(cmd)

        if dry_run:
            print(f"{self._DRY_RUN_PREFIX} {' '.join(resolved_cmd)}")
            return Ok(
                subprocess.CompletedProcess(
                    args=resolved_cmd,
                    returncode=0,
                    stdout="",
                    stderr="",
                )
            )

        full_env = {**os.environ, **(env or {})}

        try:
            result = subprocess.run(
                resolved_cmd,
                cwd=resolved_cwd,
                env=full_env,
                capture_output=True,
                text=True,
                check=True,
            )
            return Ok(result)
        except subprocess.CalledProcessError as exc:
            error_message = self._extract_error(exc, resolved_cmd)
            return Err(CommandExecutionError(" ".join(resolved_cmd), error_message))

    @staticmethod
    def _extract_error(
        exc: subprocess.CalledProcessError,
        cmd: list[str],
    ) -> str:
        detail = exc.stderr.strip() or exc.stdout.strip() or "unknown error"
        exit_code = exc.returncode

        if cmd and "git" in cmd[0]:
            git_error = SubprocessCommandRunner._extract_git_error(exc.stderr)
            if git_error:
                return git_error
            return f"exit code {exit_code}: {detail}"

        return f"exit code {exit_code}: {detail}"

    @staticmethod
    def _extract_git_error(stderr: str) -> str | None:
        for pattern, label in [
            ("couldn't find remote ref", "remote ref not found"),
            ("failed to push", "push rejected"),
            ("fetch first", "non-fast-forward push rejected"),
            ("cannot lock ref", "cannot lock ref"),
            ("already exists", "branch or tag already exists"),
            ("not a git repository", "not a git repository"),
            ("pathspec", "pathspec did not match"),
            ("nothing to commit", "nothing to commit"),
            ("did not match any file", "did not match any file"),
            ("could not apply", "could not apply"),
            ("CONFLICT", "merge conflict detected"),
            ("Please commit", "uncommitted changes present"),
            ("not our ref", "not our ref"),
            ("unable to access", "unable to access remote"),
            ("could not read Username", "authentication required"),
            ("could not read Password", "authentication required"),
            ("remote: Invalid username", "invalid credentials"),
            ("remote: Authentication failed", "authentication failed"),
            ("remote: Not Found", "remote repository not found"),
            ("remote: Repository not found", "remote repository not found"),
            (" Connection refused", "connection refused"),
            ("Could not resolve host", "could not resolve host"),
            ("Timeout", "operation timed out"),
            ("fatal:", None),
        ]:
            for line in stderr.splitlines():
                if pattern in line:
                    if label:
                        return label
                    return line.strip().removeprefix("fatal: ").strip()
        return None
