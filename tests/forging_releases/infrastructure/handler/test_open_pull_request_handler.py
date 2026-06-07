# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import pytest

from forging_releases.application.services.open_release_pull_request_service import (
    OpenReleasePullRequestService,
)
from forging_releases.domain.commands import OpenPullRequestCommand
from forging_releases.infrastructure.handler.open_pull_request_handler import (
    OpenPullRequestHandler,
)
from forging_releases.infrastructure.pull_request_service.github_pull_request_service import (
    GitHubPullRequestService,
)
from tests.fixtures.handler_scenarios import _RequestCaptureHandler


@pytest.mark.integration
class TestOpenPullRequestHandler:
    async def test_handle_when_dry_run_true_then_no_http_call(self, http_pr_server: str) -> None:
        pr_service = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake",
            base_url=http_pr_server,
        )
        use_case = OpenReleasePullRequestService(pull_request_service=pr_service)
        handler = OpenPullRequestHandler(use_case=use_case)

        command = OpenPullRequestCommand(version="1.0.0", branch="release/v1.0.0", dry_run=True)

        await handler.handle(command)

        assert _RequestCaptureHandler.received == []

    async def test_handle_when_dry_run_false_then_creates_pr_with_correct_data(
        self,
        http_pr_server: str,
    ) -> None:
        pr_service = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake",
            base_url=http_pr_server,
        )
        use_case = OpenReleasePullRequestService(pull_request_service=pr_service)
        handler = OpenPullRequestHandler(use_case=use_case)

        command = OpenPullRequestCommand(
            version="2.0.0",
            branch="release/v2.0.0",
            dry_run=False,
        )

        await handler.handle(command)

        assert len(_RequestCaptureHandler.received) == 1
        body = _RequestCaptureHandler.received[0]
        assert body["title"] == "Release v2.0.0"
        assert body["head"] == "release/v2.0.0"

    async def test_handle_when_invalid_version_then_returns_none(
        self,
        http_pr_server: str,
    ) -> None:
        pr_service = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake",
            base_url=http_pr_server,
        )
        use_case = OpenReleasePullRequestService(pull_request_service=pr_service)
        handler = OpenPullRequestHandler(use_case=use_case)

        command = OpenPullRequestCommand(
            version="not-a-version",
            branch="release/v1.0.0",
            dry_run=True,
        )

        result = await handler.handle(command)

        assert result is None

    async def test_handle_when_multiple_versions_then_each_creates_correct_input(
        self,
        http_pr_server: str,
    ) -> None:
        pr_service = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake",
            base_url=http_pr_server,
        )
        use_case = OpenReleasePullRequestService(pull_request_service=pr_service)
        handler = OpenPullRequestHandler(use_case=use_case)

        command_v1 = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )
        command_v2 = OpenPullRequestCommand(
            version="3.2.1",
            branch="release/v3.2.1",
            dry_run=False,
        )

        await handler.handle(command_v1)
        await handler.handle(command_v2)

        assert len(_RequestCaptureHandler.received) == 2
        assert _RequestCaptureHandler.received[0]["title"] == "Release v1.0.0"
        assert _RequestCaptureHandler.received[1]["title"] == "Release v3.2.1"

    async def test_handle_when_sequential_calls_then_independent_inputs(
        self,
        http_pr_server: str,
    ) -> None:
        pr_service = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake",
            base_url=http_pr_server,
        )
        use_case = OpenReleasePullRequestService(pull_request_service=pr_service)
        handler = OpenPullRequestHandler(use_case=use_case)

        cmd_a = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )
        cmd_b = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        await handler.handle(cmd_a)
        await handler.handle(cmd_b)

        assert len(_RequestCaptureHandler.received) == 2
        assert _RequestCaptureHandler.received[0] == _RequestCaptureHandler.received[1]
