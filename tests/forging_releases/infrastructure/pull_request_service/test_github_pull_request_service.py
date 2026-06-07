# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import pytest

from forging_releases.application.errors import PullRequestCreationError
from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.domain.value_objects import ReleaseBaseBranchName, ReleaseBranchName
from forging_releases.infrastructure.pull_request_service.github_pull_request_service import (
    GitHubPullRequestService,
)
from tests.fixtures.handler_scenarios import _RequestCaptureHandler


@pytest.mark.integration
class TestGitHubPullRequestService:
    def test_open_when_pr_created_then_returns_output(self, http_pr_server: str) -> None:
        svc = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake-token",
            base_url=http_pr_server,
        )
        pr = ReleasePullRequest.create(
            base=ReleaseBaseBranchName("release/v0.0.0"),
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Automated release",
            external_id=None,
        )

        result = svc.open(pr)

        assert result.is_ok is True
        output = result.value
        assert output.pr_id == "42"
        assert output.url == "https://github.com/owner/repo/pull/42"
        assert len(_RequestCaptureHandler.received) == 1
        req_body = _RequestCaptureHandler.received[0]
        assert req_body["title"] == "Release v1.0.0"
        assert req_body["head"] == "release/v1.0.0"

    def test_open_when_api_error_then_returns_err(self) -> None:
        svc = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake-token",
            base_url="http://127.0.0.1:1",
        )
        pr = ReleasePullRequest.create(
            base=ReleaseBaseBranchName("release/v0.0.0"),
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Automated release",
            external_id=None,
        )

        result = svc.open(pr)

        assert result.is_err is True
        assert isinstance(result.error, PullRequestCreationError)
