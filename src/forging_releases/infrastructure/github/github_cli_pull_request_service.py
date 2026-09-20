from urllib.parse import urlparse

from forging_releases.application.errors import (
    CommandExecutionError,
    PullRequestServiceError,
)
from forging_releases.application.ports.outbound import (
    CommandRunner,
    OpenPullRequestOutput,
    PullRequestService,
)
from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.infrastructure.commons.process import SubprocessCommandRunner


class GitHubCliPullRequestService(PullRequestService):
    """GitHub CLI-backed pull-request strategy."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner if runner is not None else SubprocessCommandRunner()

    def open(self, pull_request: ReleasePullRequest) -> OpenPullRequestOutput:
        """Create a pull request and return its URL and identifier."""
        command = [
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
        try:
            url = self._runner.run(command).strip()
        except CommandExecutionError as exc:
            detail = exc.stderr.strip() or exc.stdout.strip()
            if detail:
                detail = f"exit code {exc.returncode}: {detail}"
            else:
                detail = f"exit code {exc.returncode}"
            raise PullRequestServiceError(
                "create",
                f"Failed to create pull request with gh: {detail}",
            ) from exc
        except FileNotFoundError as exc:
            raise PullRequestServiceError(
                "create",
                f"Failed to create pull request with gh: gh is not installed or not found in PATH ({exc})",
            ) from exc
        except RuntimeError as exc:
            raise PullRequestServiceError(
                "create",
                f"Failed to create pull request with gh: {exc}",
            ) from exc

        try:
            parsed_url = urlparse(url)
            _ = parsed_url.port
        except ValueError as exc:
            raise PullRequestServiceError(
                "create",
                f"Failed to create pull request with gh: command returned an invalid pull request URL: {url!r}",
            ) from exc
        path_parts = [part for part in parsed_url.path.split("/") if part]
        if (
            parsed_url.scheme not in {"http", "https"}
            or not parsed_url.netloc
            or not parsed_url.hostname
            or parsed_url.params
            or parsed_url.query
            or parsed_url.fragment
            or len(path_parts) != 4
            or path_parts[-2] != "pull"
            or not path_parts[-1].isdigit()
        ):
            raise PullRequestServiceError(
                "create",
                f"Failed to create pull request with gh: command returned an invalid pull request URL: {url!r}",
            )

        pr_id = path_parts[-1]
        return OpenPullRequestOutput(pr_id=pr_id, url=url)
