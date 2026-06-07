"""Release pull request entity.

Provides ``ReleasePullRequest``, a domain entity representing the intent to
publish a release through a pull request from a release branch into a base
branch.
"""

from typing import Self
from uuid import UUID, uuid7

from forging_blocks.domain import Entity

from forging_releases.domain.value_objects import ReleaseBaseBranchName, ReleaseBranchName


class ReleasePullRequest(Entity[UUID]):
    """Represents the intent to publish a release.

    Domain invariants:
    - base must be a valid release base branch (enforced by ReleaseBaseBranchName type)
    - head must be a valid release branch (enforced by ReleaseBranchName type)
    """

    def __init__(
        self,
        id: UUID,
        base: ReleaseBaseBranchName,
        head: ReleaseBranchName,
        title: str,
        body: str,
        external_id: int | None,
    ) -> None:
        """Initialize a release pull request.

        Args:
            id: The unique identifier for this pull request entity.
            base: The target base branch for the pull request.
            head: The release branch to merge.
            title: The pull request title.
            body: The pull request description body.
            external_id: The external (e.g. GitHub) pull request number, or ``None``.
        """
        super().__init__(id)
        self._base = base
        self._head = head
        self._title = title
        self._body = body
        self._external_id = external_id

    @classmethod
    def create(
        cls,
        base: ReleaseBaseBranchName,
        head: ReleaseBranchName,
        title: str,
        body: str,
        external_id: int | None,
    ) -> Self:
        """Create a new ``ReleasePullRequest`` with an auto-generated UUID.

        Args:
            base: The target base branch.
            head: The release branch to merge.
            title: The pull request title.
            body: The pull request description.
            external_id: The external pull request number, or ``None``.

        Returns:
            A new ``ReleasePullRequest`` instance.
        """
        id = uuid7()

        return cls(id, base, head, title, body, external_id)

    @property
    def base(self) -> ReleaseBaseBranchName:
        """Return the target base branch."""
        return self._base

    @property
    def head(self) -> ReleaseBranchName:
        """Return the release branch to merge."""
        return self._head

    @property
    def title(self) -> str:
        """Return the pull request title."""
        return self._title

    @property
    def body(self) -> str:
        """Return the pull request description body."""
        return self._body

    @property
    def external_id(self) -> int | None:
        """Return the external pull request number, or ``None`` if not yet submitted."""
        return self._external_id
