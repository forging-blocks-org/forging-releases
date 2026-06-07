"""Application service responsible for creating the release pull request."""

from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import InvalidVersionError, PullRequestCreationError
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

type _OpenPRError = InvalidVersionError | PullRequestCreationError


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
        """Initialize the service with its required collaborator.

        Args:
            pull_request_service: Infrastructure service for creating pull requests.
        """
        self._pull_request_service = pull_request_service

    async def execute(
        self,
        request: OpenReleasePullRequestInput,
    ) -> Result[OpenReleasePullRequestOutput, _OpenPRError]:
        """Open the release pull request for the given version and branch.

        Validates the input, builds a ReleasePullRequest entity, and delegates
        creation to the infrastructure pull request service.

        Args:
            request: Input DTO containing the version, branch, and dry-run flag.

        Returns:
            Ok with OpenReleasePullRequestOutput on success,
            Err with InvalidVersionError or PullRequestCreationError on failure.
        """
        build_result = self._build_release_pull_request(request)
        match build_result:
            case Err(error=err):
                return Err(err)
            case Ok(value=pull_request):
                if request.dry_run:
                    return Ok(
                        OpenReleasePullRequestOutput(
                            pr_id=None,
                            url=None,
                        )
                    )

                pr_result = self._pull_request_service.open(pull_request)
                match pr_result:
                    case Err(error=err):
                        return Err(err)
                    case Ok(value=output):
                        return Ok(
                            OpenReleasePullRequestOutput(
                                pr_id=output.pr_id,
                                url=output.url,
                            )
                        )
                    case _:
                        return Err(PullRequestCreationError("unknown pull request error"))
            case _:
                return Err(InvalidVersionError(request.version))

    def _build_release_pull_request(
        self,
        request: OpenReleasePullRequestInput,
    ) -> Result[ReleasePullRequest, InvalidVersionError]:
        match ReleaseVersion.from_str(request.version):
            case Err():
                return Err(InvalidVersionError(request.version))
            case Ok(value=release_version):
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
            case _:
                return Err(InvalidVersionError(request.version))
