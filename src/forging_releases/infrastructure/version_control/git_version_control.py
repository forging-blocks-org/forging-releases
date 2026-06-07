from __future__ import annotations

import os
import subprocess

from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import CommandExecutionError
from forging_releases.application.ports.outbound.version_control import VersionControl
from forging_releases.domain.value_objects import ReleaseBranchName

"""Git-based version control implementation."""


class GitVersionControl(VersionControl):
    """Manages Git branches, commits, and pushes for release workflows."""

    _MAIN_BRANCH: str = "main"
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None, main_branch: str = "main") -> None:
        """Initialize the service.

        Args:
            cwd: Working directory of the Git repository.
            main_branch: Name of the main branch (default "main").
        """
        self._cwd = cwd
        self._main_branch = main_branch

    def branch_exists(self, branch: ReleaseBranchName) -> bool:
        """Check whether a local branch exists.

        Args:
            branch: The branch to check.

        Returns:
            True if the local branch exists.
        """
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
    ) -> Result[None, CommandExecutionError]:
        """Checkout an existing branch.

        Args:
            branch: The branch to check out.
            dry_run: If True, only log the intended command.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        return self._run_git_result(
            ["checkout", branch.value],
            dry_run=dry_run,
        )

    def checkout_main(self) -> Result[None, CommandExecutionError]:
        """Checkout the main branch.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        return self._run_git_result(["checkout", self._main_branch])

    def commit_release_artifacts(
        self, *, dry_run: bool = False
    ) -> Result[None, CommandExecutionError]:
        """Stage all changes and create a release commit.

        Args:
            dry_run: If True, only log the intended commands.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        add_result = self._run_git_result(
            ["add", "."],
            dry_run=dry_run,
        )
        if add_result.is_err and not dry_run:
            return add_result

        return self._run_git_result(
            ["commit", "--no-edit", "--allow-empty", "-m", "chore: release"],
            dry_run=dry_run,
        )

    def create_branch(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> Result[None, CommandExecutionError]:
        """Create and switch to a new branch.

        Args:
            branch: The name of the branch to create.
            dry_run: If True, only log the intended command.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        return self._run_git_result(
            ["checkout", "-b", branch.value],
            dry_run=dry_run,
        )

    def delete_local_branch(self, branch: ReleaseBranchName) -> Result[None, CommandExecutionError]:
        """Delete a local branch.

        Args:
            branch: The branch to delete.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        return self._run_git_result(
            ["branch", "-D", branch.value],
            check=False,
        )

    def delete_remote_branch(
        self, branch: ReleaseBranchName
    ) -> Result[None, CommandExecutionError]:
        """Delete a remote branch via git push.

        Args:
            branch: The branch to delete on the remote.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        return self._run_git_result(
            ["push", "origin", "--delete", branch.value],
            check=False,
        )

    def push(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> Result[None, CommandExecutionError]:
        """Push a branch and tags to the remote.

        Args:
            branch: The branch to push.
            dry_run: If True, only log the intended commands.

        Returns:
            Ok(None) on success, Err with CommandExecutionError on failure.
        """
        push_result = self._run_git_result(
            ["push", "--set-upstream", "origin", branch.value],
            dry_run=dry_run,
        )
        if push_result.is_err and not dry_run:
            return push_result

        return self._run_git_result(
            ["push", "--tags"],
            dry_run=dry_run,
        )

    def remote_branch_exists(self, branch: ReleaseBranchName) -> bool:
        """Check whether a remote branch exists.

        Args:
            branch: The branch to check.

        Returns:
            True if the remote branch exists.
        """
        result = self._run_git(
            ["ls-remote", "--heads", "origin", branch.value],
            check=False,
        )
        return bool(result.stdout.strip())

    def _run_git(
        self,
        args: list[str],
        *,
        dry_run: bool = False,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        cmd = ["git", *args]

        if dry_run:
            print(f"{self._DRY_RUN_PREFIX} {' '.join(cmd)}")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr="",
            )

        clean_env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env = {
            **clean_env,
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

    def _run_git_result(
        self,
        args: list[str],
        *,
        dry_run: bool = False,
        check: bool = True,
    ) -> Result[None, CommandExecutionError]:
        try:
            self._run_git(args, dry_run=dry_run, check=check)
            return Ok(None)
        except subprocess.CalledProcessError as exc:
            cmd_str = " ".join(["git", *args])
            detail = exc.stderr.strip() or exc.stdout.strip() or "unknown error"
            return Err(CommandExecutionError(cmd_str, detail))
