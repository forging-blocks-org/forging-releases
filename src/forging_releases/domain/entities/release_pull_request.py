from dataclasses import dataclass

from forging_releases.domain.errors import InvalidReleasePullRequestError
from forging_releases.domain.value_objects import ReleaseBranchName


@dataclass(frozen=True)
class ReleasePullRequest:
    """Represents the intent to publish a release.

    Domain invariants:
    - base must be a non-empty branch name.
    - head must be a valid release branch (enforced by ReleaseBranchName type)
    """

    base: str
    head: ReleaseBranchName
    title: str
    body: str

    def __post_init__(self) -> None:
        if not self.base.strip():
            raise InvalidReleasePullRequestError("Base branch must not be empty")
