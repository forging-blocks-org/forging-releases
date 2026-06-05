"""Git implementation of the VersionControl outbound port.

Uses subprocess to call git CLI — no GitPython dependency needed.
All commands are non-interactive (--no-pager, --no-edit, GIT_* env vars).
"""

from __future__ import annotations

import os
import subprocess

from forging_releases.application.ports.outbound.version_control import VersionControl
from forging_releases.domain.value_objects import ReleaseBranchName


class GitVersionControl(VersionControl):
    """Non-interactive git CLI adapter.

    Guarantees:
    - All commands disable paging, prompting, and interactive editors.
    - Failures propagate as subprocess.CalledProcessError.
    - dry_run=True logs the command but does not execute it.
    """

    _DEFAULT_MAIN_BRANCH: str = "main"
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None, main_branch: str = "main") -> None:
        self._cwd = cwd
        self._main_branch = main_branch

    # ----------------------------------------------------------------
    # Implementation
    # ----------------------------------------------------------------

    def branch_exists(self, branch: ReleaseBranchName) -> bool:
        """Check if a local branch exists."""
        result = self._run_git(
            ["rev-parse", "--verify", "--quiet", branch.value],
            check=False,
        )
        return result.returncode == 0

    def checkout(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> None:
        """Checkout an existing local branch."""
        self._run_git(
            ["checkout", branch.value],
            dry_run=dry_run,
        )

    def checkout_main(self) -> None:
        """Return to the default branch."""
        self._run_git(["checkout", self._main_branch])

    def commit_release_artifacts(self, *, dry_run: bool = False) -> None:
        """Commit version bump and generated artifacts."""
        self._run_git(
            ["add", "."],
            dry_run=dry_run,
        )
        self._run_git(
            ["commit", "--no-edit", "--allow-empty", "-m", "chore: release"],
            dry_run=dry_run,
        )

    def create_branch(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> None:
        """Create and checkout a new local branch."""
        self._run_git(
            ["checkout", "-b", branch.value],
            dry_run=dry_run,
        )

    def delete_local_branch(self, branch: ReleaseBranchName) -> None:
        """Delete a local branch if present."""
        self._run_git(
            ["branch", "-D", branch.value],
            check=False,
        )

    def delete_remote_branch(self, branch: ReleaseBranchName) -> None:
        """Delete a remote branch (origin). Non-interactive."""
        self._run_git(
            ["push", "origin", "--delete", branch.value],
            check=False,
        )

    def push(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> None:
        """Push branch and tags to origin."""
        self._run_git(
            ["push", "--set-upstream", "origin", branch.value],
            dry_run=dry_run,
        )
        self._run_git(
            ["push", "--tags"],
            dry_run=dry_run,
        )

    def remote_branch_exists(self, branch: ReleaseBranchName) -> bool:
        """Check if a remote branch exists on origin."""
        result = self._run_git(
            ["ls-remote", "--heads", "origin", branch.value],
            check=False,
        )
        return bool(result.stdout.strip())

    # ----------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------

    def _run_git(
        self,
        args: list[str],
        *,
        dry_run: bool = False,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Execute a git command in the configured working directory.

        Args:
            args: git sub-command arguments (e.g. ["checkout", "main"]).
            dry_run: If True, only log the command and return a dummy result.
            check: If True, raise CalledProcessError on non-zero exit.
        """
        cmd = ["git", *args]

        if dry_run:
            print(f"{self._DRY_RUN_PREFIX} {' '.join(cmd)}")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr="",
            )

        env = {
            **os.environ,
            "GIT_PAGER": "cat",
            "GIT_EDITOR": "true",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Release Bot",
            "GIT_AUTHOR_EMAIL": "release@forging-blocks.org",
            "GIT_COMMITTER_NAME": "Release Bot",
            "GIT_COMMITTER_EMAIL": "release@forging-blocks.org",
        }

        return subprocess.run(
            cmd,
            cwd=self._cwd,
            env=env,
            capture_output=True,
            text=True,
            check=check,
        )
