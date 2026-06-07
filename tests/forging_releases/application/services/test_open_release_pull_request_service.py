# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
from unittest.mock import Mock

import pytest

from forging_blocks.foundation import Ok

from forging_releases.application.errors import InvalidVersionError
from forging_releases.application.ports.inbound.open_release_pull_request_use_case import (
    OpenReleasePullRequestInput,
)
from forging_releases.application.ports.outbound.pull_request_service import (
    OpenPullRequestOutput,
    PullRequestService,
)
from forging_releases.application.services.open_release_pull_request_service import (
    OpenReleasePullRequestService,
)


@pytest.mark.unit
class TestOpenReleasePullRequestService:
    async def test_execute_when_dry_run_then_returns_empty_output(self) -> None:
        pull_request_service = Mock(spec=PullRequestService)
        service = OpenReleasePullRequestService(
            pull_request_service=pull_request_service,
        )

        request = OpenReleasePullRequestInput(
            version="1.0.0", branch="release/v1.0.0", dry_run=True
        )

        result = await service.execute(request)  # type: ignore[reportArgumentType]

        assert result.is_ok is True
        assert result.value.pr_id is None
        assert result.value.url is None
        pull_request_service.open.assert_not_called()

    async def test_execute_when_not_dry_run_then_calls_pull_request_service(self) -> None:
        mock_output = OpenPullRequestOutput(pr_id="42", url="https://github.com/org/repo/pull/42")
        pull_request_service = Mock(spec=PullRequestService)
        pull_request_service.open.return_value = Ok(mock_output)
        service = OpenReleasePullRequestService(
            pull_request_service=pull_request_service,
        )

        request = OpenReleasePullRequestInput(
            version="1.0.0", branch="release/v1.0.0", dry_run=False
        )

        result = await service.execute(request)  # type: ignore[reportArgumentType]

        assert result.is_ok is True
        assert result.value.pr_id == "42"
        assert result.value.url == "https://github.com/org/repo/pull/42"
        pull_request_service.open.assert_called_once()

    async def test_execute_when_pull_request_service_returns_none_ids_then_mapped(self) -> None:
        mock_output = OpenPullRequestOutput(pr_id=None, url=None)
        pull_request_service = Mock(spec=PullRequestService)
        pull_request_service.open.return_value = Ok(mock_output)
        service = OpenReleasePullRequestService(
            pull_request_service=pull_request_service,
        )

        request = OpenReleasePullRequestInput(
            version="0.1.0", branch="release/v0.1.0", dry_run=False
        )

        result = await service.execute(request)  # type: ignore[reportArgumentType]

        assert result.is_ok is True
        assert result.value.pr_id is None
        assert result.value.url is None

    async def test_execute_when_invalid_version_then_returns_err(self) -> None:
        pull_request_service = Mock(spec=PullRequestService)
        service = OpenReleasePullRequestService(
            pull_request_service=pull_request_service,
        )

        request = OpenReleasePullRequestInput(
            version="not-a-version", branch="release/v1.0.0", dry_run=True
        )

        result = await service.execute(request)  # type: ignore[reportArgumentType]

        assert result.is_err is True
        assert isinstance(result.error, InvalidVersionError)
        assert "not-a-version" in result.error.message.value
