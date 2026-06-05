from typing import cast

from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import InvalidVersionError
from forging_releases.application.ports.inbound import (
    OpenReleasePullRequestInput,
    OpenReleasePullRequestOutput,
    OpenReleasePullRequestUseCase,
)
from forging_releases.application.ports.outbound import (
    PullRequestService,
)
from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.domain.value_objects import (
    ReleaseBaseBranchName,
    ReleaseBranchName,
    ReleaseVersion,
)


class OpenReleasePullRequestService(OpenReleasePullRequestUseCase):
    """Application service responsible for opening the release pull request.

    Responsibilities:
    - validate raw inputs
    - build ReleasePullRequest entity
    - delegate to infrastructure
    """

    def __init__(
        self,
        *,
        pull_request_service: PullRequestService,
    ) -> None:
        self._pull_request_service = pull_request_service

    async def execute(
        self,
        request: OpenReleasePullRequestInput,
    ) -> Result[OpenReleasePullRequestOutput, InvalidVersionError]:
        result = self._build_release_pull_request(request)
        if result.is_err:
            return Err(cast(InvalidVersionError, result.error))
        pull_request = cast(ReleasePullRequest, result.value)

        if request.dry_run:
            return Ok(
                OpenReleasePullRequestOutput(
                    pr_id=None,
                    url=None,
                )
            )

        output = self._pull_request_service.open(pull_request)

        return Ok(
            OpenReleasePullRequestOutput(
                pr_id=output.pr_id,
                url=output.url,
            )
        )

    def _build_release_pull_request(
        self,
        request: OpenReleasePullRequestInput,
    ) -> Result[ReleasePullRequest, InvalidVersionError]:
        version_result = ReleaseVersion.from_str(request.version)
        if version_result.is_err:
            return Err(InvalidVersionError(request.version))
        release_version = cast(ReleaseVersion, version_result.value)

        branch = ReleaseBranchName(request.branch)

        return Ok(
            ReleasePullRequest.create(
                base=ReleaseBaseBranchName("release/v0.0.0"),
                head=branch,
                title=f"Release v{release_version.value}",
                body=f"Automated release pull request for version {release_version.value}.",
                external_id=None,
            )
        )
