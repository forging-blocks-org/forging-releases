from abc import abstractmethod

from forging_blocks.foundation import OutputPort, Result

from forging_releases.application.errors import CommandExecutionError
from forging_releases.domain.value_objects import ReleaseBranchName


class VersionControl(OutputPort):
    """Abstracts version control operations required by the release workflow.

    Must be non-interactive.
    """

    @abstractmethod
    def branch_exists(
        self,
        branch: ReleaseBranchName,
    ) -> bool:
        """Local branch existence check."""
        ...

    @abstractmethod
    def checkout(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> Result[None, CommandExecutionError]:
        """Checkout local branch."""
        ...

    @abstractmethod
    def checkout_main(self) -> Result[None, CommandExecutionError]:
        """Return to the main branch (or the configured default branch)."""
        ...

    @abstractmethod
    def commit_release_artifacts(
        self,
        *,
        dry_run: bool = False,
    ) -> Result[None, CommandExecutionError]:
        """Commit the version bump and any generated artifacts (e.g., changelog).
        Must be non-interactive.
        """
        ...

    @abstractmethod
    def create_branch(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> Result[None, CommandExecutionError]:
        """Create local branch."""
        ...

    @abstractmethod
    def delete_local_branch(
        self,
        branch: ReleaseBranchName,
    ) -> Result[None, CommandExecutionError]:
        """Delete local branch if present."""
        ...

    @abstractmethod
    def delete_remote_branch(
        self,
        branch: ReleaseBranchName,
    ) -> Result[None, CommandExecutionError]:
        """Delete remote branch (origin) if present.
        Must be implemented as a non-interactive command (e.g., git push origin :branch).
        """
        ...

    @abstractmethod
    def push(
        self,
        branch: ReleaseBranchName,
        *,
        dry_run: bool = False,
    ) -> Result[None, CommandExecutionError]:
        """Push branch and tag."""
        ...

    @abstractmethod
    def remote_branch_exists(
        self,
        branch: ReleaseBranchName,
    ) -> bool:
        """Remote existence check (origin/<branch>).
        This is important for idempotency and avoiding non-fast-forward surprises.
        """
        ...
