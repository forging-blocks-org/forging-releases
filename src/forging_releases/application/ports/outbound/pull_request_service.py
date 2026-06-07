from abc import abstractmethod
from dataclasses import dataclass

from forging_blocks.foundation import OutputPort, Result

from forging_releases.application.errors import PullRequestCreationError
from forging_releases.domain.entities import ReleasePullRequest


@dataclass(frozen=True)
class OpenPullRequestOutput:
    """DTO representing the output of creating a pull request."""

    pr_id: str | None
    url: str | None


class PullRequestService(OutputPort):
    """Service that manages pull request creation in remote repository."""

    @abstractmethod
    def open(
        self,
        pull_request: ReleasePullRequest,
    ) -> Result[OpenPullRequestOutput, PullRequestCreationError]:
        """Open a pull request and return its details.

        Returns:
            Ok(OpenPullRequestOutput) if the PR was created successfully,
            Err(PullRequestCreationError) if the remote API call failed.
        """
        ...
