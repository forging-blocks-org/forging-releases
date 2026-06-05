# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
from dataclasses import FrozenInstanceError

import pytest

from forging_releases.application.ports.inbound.open_release_pull_request_use_case import (
    OpenReleasePullRequestInput,
    OpenReleasePullRequestOutput,
)


@pytest.mark.unit
class TestOpenReleasePullRequestInput:
    def test_init_when_created_with_required_fields_then_stores_values(self) -> None:
        request = OpenReleasePullRequestInput(version="1.0.0", branch="release/v1.0.0")

        assert request.version == "1.0.0"
        assert request.branch == "release/v1.0.0"
        assert request.dry_run is False

    def test_init_when_dry_run_true_then_stored(self) -> None:
        request = OpenReleasePullRequestInput(
            version="1.0.0", branch="release/v1.0.0", dry_run=True
        )

        assert request.dry_run is True

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        request = OpenReleasePullRequestInput(version="1.0.0", branch="release/v1.0.0")

        with pytest.raises(FrozenInstanceError):
            request.version = "2.0.0"  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        r1 = OpenReleasePullRequestInput(version="1.0.0", branch="release/v1.0.0")
        r2 = OpenReleasePullRequestInput(version="1.0.0", branch="release/v1.0.0")

        assert r1 == r2

    def test_eq_when_different_version_then_not_equal(self) -> None:
        r1 = OpenReleasePullRequestInput(version="1.0.0", branch="release/v1.0.0")
        r2 = OpenReleasePullRequestInput(version="2.0.0", branch="release/v1.0.0")

        assert r1 != r2


@pytest.mark.unit
class TestOpenReleasePullRequestOutput:
    def test_init_when_created_with_values_then_stores_all(self) -> None:
        output = OpenReleasePullRequestOutput(pr_id="42", url="https://github.com/org/repo/pull/42")

        assert output.pr_id == "42"
        assert output.url == "https://github.com/org/repo/pull/42"

    def test_init_when_created_with_none_values_then_stores_none(self) -> None:
        output = OpenReleasePullRequestOutput(pr_id=None, url=None)

        assert output.pr_id is None
        assert output.url is None

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        output = OpenReleasePullRequestOutput(pr_id="1", url="http://example.com")

        with pytest.raises(FrozenInstanceError):
            output.pr_id = "2"  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        o1 = OpenReleasePullRequestOutput(pr_id="1", url="http://example.com")
        o2 = OpenReleasePullRequestOutput(pr_id="1", url="http://example.com")

        assert o1 == o2

    def test_eq_when_different_then_not_equal(self) -> None:
        o1 = OpenReleasePullRequestOutput(pr_id="1", url="http://example.com")
        o2 = OpenReleasePullRequestOutput(pr_id="2", url="http://example.com")

        assert o1 != o2
