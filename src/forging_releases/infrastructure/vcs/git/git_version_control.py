import logging
from collections.abc import Sequence

from forging_releases.application.errors import CommandExecutionError, VersionControlError
from forging_releases.application.ports.outbound import CommandRunner, VersionControl
from forging_releases.domain.value_objects import ReleaseBranchName


class GitVersionControl(VersionControl):
    """Git-backed version-control strategy."""

    def __init__(
        self,
        runner: CommandRunner,
        *,
        base_branch: str = "main",
        remote: str = "origin",
        release_branch_prefix: str = "release/v",
    ) -> None:
        self._runner = runner
        self._base_branch = base_branch
        self._remote = remote
        self._release_branch_prefix = release_branch_prefix

    def branch_exists(self, branch: ReleaseBranchName) -> bool:
        """Return whether a local branch exists."""
        logging.info("Checking if branch %s exists...", branch.value)
        try:
            self._runner.run(["git", "rev-parse", "--verify", branch.value])
        except CommandExecutionError:
            logging.info("[OK] Branch %s does not exist", branch.value)
            return False
        except FileNotFoundError as exc:
            raise VersionControlError(
                "branch lookup",
                f"Git branch lookup failed: git is not installed or not found in PATH ({exc})",
            ) from exc
        logging.info("[OK] Branch %s exists", branch.value)
        return True

    def checkout(self, branch: ReleaseBranchName, *, dry_run: bool = False) -> None:
        """Checkout an existing local branch."""
        if dry_run:
            return
        logging.info("Checking out branch %s...", branch.value)
        self._run(["git", "checkout", branch.value], operation="checkout")
        logging.info("[OK] Checked out branch %s", branch.value)

    def checkout_main(self) -> None:
        """Checkout the configured base branch, resolving the remote default as fallback."""
        logging.info("Checking out %s branch...", self._base_branch)
        try:
            self._run(["git", "checkout", self._base_branch], operation="checkout")
        except VersionControlError as exc:
            if not self._is_missing_base_branch_error(exc):
                raise
            raw = self._run(
                [
                    "git",
                    "symbolic-ref",
                    "--short",
                    f"refs/remotes/{self._remote}/HEAD",
                ],
                operation="remote lookup",
            ).strip()
            remote_prefix = f"{self._remote}/"
            default_branch = raw.removeprefix(remote_prefix)
            self._run(["git", "checkout", default_branch], operation="checkout")
            logging.info("[OK] Checked out %s branch", default_branch)
        else:
            logging.info("[OK] Checked out %s branch", self._base_branch)

    def commit_release_artifacts(self, *, dry_run: bool = False) -> None:
        """Stage and commit release artifacts, retrying once after hook changes."""
        if dry_run:
            return
        logging.info("Committing release artifacts...")
        try:
            self._run(["git", "add", "-A"], operation="commit")
            self._run(
                ["git", "commit", "-m", "chore(release): prepare release"],
                operation="commit",
            )
        except VersionControlError as exc:
            if not self._is_pre_commit_failure(str(exc)):
                raise
            try:
                self._run(["git", "add", "-A"], operation="commit")
                self._run(
                    ["git", "commit", "-m", "chore(release): prepare release"],
                    operation="commit",
                )
            except VersionControlError:
                raise
        logging.info("[OK] Committed release artifacts")

    def create_branch(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> None:
        """Create and checkout a release branch."""
        if dry_run:
            return
        logging.info("Creating release branch %s...", branch.value)
        self._run(
            ["git", "checkout", "-b", branch.value],
            operation="branch creation",
        )
        logging.info("[OK] Created branch %s", branch.value)

    def delete_local_branch(self, branch: ReleaseBranchName) -> None:
        """Delete a local release branch."""
        self._run(
            ["git", "branch", "-D", branch.value],
            operation="branch deletion",
            check=False,
        )

    def delete_remote_branch(self, branch: ReleaseBranchName) -> None:
        """Delete a release branch from the configured remote."""
        self._run(
            ["git", "push", self._remote, "--delete", branch.value],
            operation="branch deletion",
            check=False,
        )

    def push(self, branch: ReleaseBranchName, *, dry_run: bool = False) -> None:
        """Push a release branch to the configured remote."""
        if dry_run:
            return
        self._run(
            ["git", "push", self._remote, branch.value],
            operation="push",
        )

    def remote_branch_exists(self, branch: ReleaseBranchName) -> bool:
        """Return whether a branch exists on the configured remote."""
        try:
            self._runner.run(
                ["git", "ls-remote", "--exit-code", "--heads", self._remote, branch.value]
            )
        except CommandExecutionError:
            return False
        except FileNotFoundError as exc:
            raise VersionControlError(
                "remote lookup",
                f"Git remote lookup failed: git is not installed or not found in PATH ({exc})",
            ) from exc
        return True

    def _run(self, command: Sequence[str], *, operation: str, check: bool = True) -> str:
        try:
            return self._runner.run(command, check=check)
        except CommandExecutionError as exc:
            detail = exc.stderr.strip() or exc.stdout.strip()
            if detail:
                detail = f"exit code {exc.returncode}: {detail}"
            else:
                detail = f"exit code {exc.returncode}"
            raise VersionControlError(operation, f"Git {operation} failed: {detail}") from exc
        except FileNotFoundError as exc:
            raise VersionControlError(
                operation,
                f"Git {operation} failed: git is not installed or not found in PATH ({exc})",
            ) from exc

    def _is_missing_base_branch_error(self, error: VersionControlError) -> bool:
        cause = error.__cause__
        if not isinstance(cause, CommandExecutionError):
            return False
        if cause.command != ("git", "checkout", self._base_branch):
            return False
        stderr = cause.stderr.lower()
        return cause.returncode == 1 and "pathspec" in stderr and "did not match" in stderr

    def _is_pre_commit_failure(self, error_msg: str) -> bool:
        indicators = ["pre-commit", "hook", "end-of-file-fixer", "ruff", "trim trailing"]
        return any(indicator in error_msg.lower() for indicator in indicators)
