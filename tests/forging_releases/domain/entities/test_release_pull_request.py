# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest
from uuid import uuid4

from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.domain.errors import InvalidReleasePullRequestError
from forging_releases.domain.value_objects import (
    ReleaseBranchName,
)


@pytest.mark.unit
class TestReleasePullRequest:
    def test_create_when_valid_args_then_success(self) -> None:
        head = ReleaseBranchName("release/v1.2.3")

        pr = ReleasePullRequest.create(
            base="main",
            head=head,
            title="Release v1.2.3",
            body="Release notes",
            external_id=None,
        )

        assert pr.base == "main"
        assert pr.head.value == "release/v1.2.3"
        assert pr.title == "Release v1.2.3"
        assert pr.body == "Release notes"
        assert pr.external_id is None
        assert pr.id is not None

    def test_init_when_valid_args_then_success(self) -> None:
        pr_id = uuid4()
        head = ReleaseBranchName("release/v1.2.3")

        pr = ReleasePullRequest(
            id=pr_id,
            base="main",
            head=head,
            title="Release v1.2.3",
            body="Release notes",
            external_id=123,
        )

        assert pr.id == pr_id
        assert pr.base == "main"
        assert pr.head.value == "release/v1.2.3"
        assert pr.title == "Release v1.2.3"
        assert pr.body == "Release notes"
        assert pr.external_id == 123

    def test_init_when_external_id_is_none_then_success(self) -> None:
        pr = ReleasePullRequest(
            id=uuid4(),
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Notes",
            external_id=None,
        )

        assert pr.external_id is None

    def test_create_when_called_then_generates_uuid(self) -> None:
        pr = ReleasePullRequest.create(
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Notes",
            external_id=None,
        )

        assert pr.id is not None

    def test_create_when_called_twelve_then_different_ids(self) -> None:
        pr1 = ReleasePullRequest.create(
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Notes",
            external_id=None,
        )
        pr2 = ReleasePullRequest.create(
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Notes",
            external_id=None,
        )

        assert pr1.id != pr2.id

    def test_equality_when_same_id_then_equal(self) -> None:
        pr_id = uuid4()
        pr1 = ReleasePullRequest(
            id=pr_id,
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="t",
            body="b",
            external_id=None,
        )
        pr2 = ReleasePullRequest(
            id=pr_id,
            base="develop",
            head=ReleaseBranchName("release/v2.0.0"),
            title="t2",
            body="b2",
            external_id=99,
        )

        assert pr1 == pr2

    def test_equality_when_different_id_then_not_equal(self) -> None:
        pr1 = ReleasePullRequest(
            id=uuid4(),
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="t",
            body="b",
            external_id=None,
        )
        pr2 = ReleasePullRequest(
            id=uuid4(),
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="t",
            body="b",
            external_id=None,
        )

        assert pr1 != pr2

    def test_is_persisted_when_created_then_true(self) -> None:
        pr = ReleasePullRequest.create(
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="t",
            body="b",
            external_id=None,
        )

        assert pr.is_persisted() is True

    def test_str_when_called_then_returns_representation(self) -> None:
        pr_id = uuid4()
        pr = ReleasePullRequest(
            id=pr_id,
            base="main",
            head=ReleaseBranchName("release/v1.0.0"),
            title="t",
            body="b",
            external_id=None,
        )

        assert str(pr) == f"ReleasePullRequest(id={pr_id})"

    def test_invalid_release_pull_request_error_when_instantiated_then_has_message(
        self,
    ) -> None:
        error = InvalidReleasePullRequestError("base must be 'main'")

        assert "base must be 'main'" in str(error)
