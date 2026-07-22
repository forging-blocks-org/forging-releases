<<<<<<< Updated upstream
"""Release pull request entity"""

from typing import Self
from uuid import UUID, uuid7

from forging_blocks.domain import Entity

from forging_releases.domain.value_objects import ReleaseBaseBranchName, ReleaseBranchName
=======
from dataclasses import dataclass

from forging_releases.domain.errors import InvalidReleasePullRequestError
from forging_releases.domain.value_objects import ReleaseBranchName
>>>>>>> Stashed changes


@dataclass(frozen=True)
class ReleasePullRequest:
    """Represents the intent to publish a release.

    Domain invariants:
    - base must be "main"
    - head must be a valid release branch (enforced by ReleaseBranchName type)
    """

<<<<<<< Updated upstream
    def __init__(
        self,
        id: UUID,
        base: ReleaseBaseBranchName,
        head: ReleaseBranchName,
        title: str,
        body: str,
        external_id: int | None,
    ) -> None:
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
        id = uuid7()

        return cls(id, base, head, title, body, external_id)

    @property
    def base(self) -> ReleaseBaseBranchName:
        return self._base

    @property
    def head(self) -> ReleaseBranchName:
        return self._head

    @property
    def title(self) -> str:
        return self._title

    @property
    def body(self) -> str:
        return self._body

    @property
    def external_id(self) -> int | None:
        return self._external_id
=======
    base: str
    head: ReleaseBranchName
    title: str
    body: str

    def __post_init__(self) -> None:
        if self.base != "main":
            raise InvalidReleasePullRequestError("Base branch must be main")
>>>>>>> Stashed changes
