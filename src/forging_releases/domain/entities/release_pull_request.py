from dataclasses import dataclass

from forging_releases.domain.errors import InvalidReleasePullRequestError
from forging_releases.domain.value_objects import ReleaseBranchName


@dataclass(frozen=True)
class ReleasePullRequest:
    """Represents the intent to publish a release.

    Domain invariants:
    - base must be "main"
    - head must be a valid release branch (enforced by ReleaseBranchName type)
    """

    base: str
    head: ReleaseBranchName
    title: str
    body: str

    def __post_init__(self) -> None:
        if self.base != "main":
            raise InvalidReleasePullRequestError("Base branch must be main")
