from __future__ import annotations

import pytest
from forging_releases.application.errors import CommandExecutionError, PullRequestServiceError
from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.github.github_cli_pull_request_service import (
    GitHubCliPullRequestService,
)

from tests.fixtures.fake_command_runner import FakeCommandRunner


@pytest.mark.unit
class TestGitHubCliPullRequestServiceEdgeCases:
    def test_open_strips_runner_whitespace_before_extracting_id(self) -> None:
        runner = FakeCommandRunner("  https://github.com/org/repo/pull/204/\n")
        service = GitHubCliPullRequestService(runner)
        pull_request = ReleasePullRequest(
            base="trunk",
            head=ReleaseBranchName("release/v2.0.4"),
            title="Release v2.0.4",
            body="Release notes",
        )

        result = service.open(pull_request)

        assert result.url == "https://github.com/org/repo/pull/204/"
        assert result.pr_id == "204"

    def test_open_includes_actual_exit_code_when_gh_fails(self) -> None:
        runner = FakeCommandRunner(
            CommandExecutionError(
                ("gh", "pr", "create"),
                13,
                "",
                "permission denied",
            )
        )
        service = GitHubCliPullRequestService(runner)
        pull_request = ReleasePullRequest(
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Release notes",
        )

        with pytest.raises(PullRequestServiceError) as exc_info:
            service.open(pull_request)

        assert exc_info.value.operation == "create"
        assert "13" in exc_info.value.message.value
        assert "permission denied" in exc_info.value.message.value
