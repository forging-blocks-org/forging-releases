"""Defines the inbound port (use case interface) for opening a release pull request."""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass

from forging_blocks.application.ports import UseCase
from forging_blocks.foundation import Result

from forging_releases.application.errors import InvalidVersionError, PullRequestCreationError


@dataclass(frozen=True)
class OpenReleasePullRequestInput:
    """Request DTO for creating a release pull request.

    All values are raw primitives.
    Validation and conversion to Value Objects
    happens inside the use case.

    Future options (intentionally not modeled yet):
    - labels: list[str]
    - reviewers: list[str]
    - draft: bool
    """

    version: str
    branch: str
    dry_run: bool = False


@dataclass(frozen=True)
class OpenReleasePullRequestOutput:
    """Response DTO for creating a release pull request."""

    pr_id: str | None
    url: str | None


type _OpenPRError = InvalidVersionError | PullRequestCreationError


class OpenReleasePullRequestUseCase(
    UseCase[
        OpenReleasePullRequestInput,
        Result[OpenReleasePullRequestOutput, _OpenPRError],
    ]
):
    """Creates the release pull request representing
    the intent to publish a new version.

    Notes:
    - The PR is the boundary between application logic and CI/CD
    - A merged PR triggers publishing and documentation deployment
    """

    @abstractmethod
    async def execute(
        self,
        request: OpenReleasePullRequestInput,
    ) -> Result[OpenReleasePullRequestOutput, _OpenPRError]:
        """Create the release pull request for the given version.

        Args:
            request: Input DTO with the version, branch, and dry-run flag.

        Returns:
            Ok with OpenReleasePullRequestOutput on success,
            Err with InvalidVersionError or PullRequestCreationError on failure.
        """
        ...
