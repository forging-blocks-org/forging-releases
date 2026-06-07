from __future__ import annotations

import os
import subprocess


class SubprocessCommandRunner:
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None) -> None:
        self._cwd = cwd

    def run(
        self,
        cmd: list[str],
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        resolved_cwd = cwd or self._cwd
        resolved_cmd = list(cmd)

        if dry_run:
            print(f"{self._DRY_RUN_PREFIX} {' '.join(resolved_cmd)}")
            return subprocess.CompletedProcess(
                args=resolved_cmd,
                returncode=0,
                stdout="",
                stderr="",
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
            return result
        except subprocess.CalledProcessError as exc:
            error_message = self._extract_error(exc, resolved_cmd)
            raise RuntimeError(error_message) from exc

    @staticmethod
    def _extract_error(
        exc: subprocess.CalledProcessError,
        cmd: list[str],
    ) -> str:
        command_str = " ".join(cmd)
        detail = exc.stderr.strip() or exc.stdout.strip() or "unknown error"
        exit_code = exc.returncode
        base = f"Command failed with exit code {exit_code}: {detail}"

        if cmd and "git" in cmd[0]:
            git_error = SubprocessCommandRunner._extract_git_error(exc.stderr)
            if git_error:
                return f"Git command failed: {git_error} (command: {command_str})"
            return f"Git command failed: {base} (command: {command_str})"

        return f"{base} (command: {command_str})"

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
