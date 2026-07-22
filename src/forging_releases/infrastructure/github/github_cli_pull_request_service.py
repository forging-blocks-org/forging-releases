from forging_releases.application.ports.outbound import (
    OpenPullRequestOutput,
    PullRequestService,
)
from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.infrastructure.commons.process import CommandRunner, SubprocessCommandRunner


class GitHubCliPullRequestService(PullRequestService):
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner if runner is not None else SubprocessCommandRunner()

    def open(self, pull_request: ReleasePullRequest) -> OpenPullRequestOutput:
        url = self._runner.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                pull_request.base,
                "--head",
                pull_request.head.value,
                "--title",
                pull_request.title,
                "--body",
                pull_request.body,
            ]
        )

        pr_id = url.rstrip("/").split("/")[-1]

        return OpenPullRequestOutput(
            pr_id=pr_id,
            url=url,
        )
