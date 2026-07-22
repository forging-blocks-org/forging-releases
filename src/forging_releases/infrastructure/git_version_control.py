from __future__ import annotations

import os
import subprocess

from forging_releases.application.ports.outbound.version_control import VersionControl
from forging_releases.domain.value_objects import ReleaseBranchName


class GitVersionControl(VersionControl):
    _MAIN_BRANCH: str = "main"
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None, main_branch: str = "main") -> None:
        self._cwd = cwd
        self._main_branch = main_branch

    def branch_exists(self, branch: ReleaseBranchName) -> bool:
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
        self._run_git(
            ["checkout", branch.value],
            dry_run=dry_run,
        )

    def checkout_main(self) -> None:
        self._run_git(["checkout", self._main_branch])

    def commit_release_artifacts(self, *, dry_run: bool = False) -> None:
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
        self._run_git(
            ["checkout", "-b", branch.value],
            dry_run=dry_run,
        )

    def delete_local_branch(self, branch: ReleaseBranchName) -> None:
        self._run_git(
            ["branch", "-D", branch.value],
            check=False,
        )

    def delete_remote_branch(self, branch: ReleaseBranchName) -> None:
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
        self._run_git(
            ["push", "--set-upstream", "origin", branch.value],
            dry_run=dry_run,
        )
        self._run_git(
            ["push", "--tags"],
            dry_run=dry_run,
        )

    def remote_branch_exists(self, branch: ReleaseBranchName) -> bool:
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
