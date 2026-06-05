# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
from dataclasses import FrozenInstanceError

import pytest

from forging_releases.application.workflow import ReleaseContext
from forging_releases.domain.value_objects import (
    ReleaseBranchName,
    ReleaseVersion,
    TagName,
)


@pytest.mark.unit
class TestReleaseContext:
    def test_init_when_created_then_stores_all_fields(self) -> None:
        version = ReleaseVersion(1, 2, 3)
        previous_version = ReleaseVersion(1, 2, 2)
        branch = ReleaseBranchName("release/v1.2.3")
        tag = TagName("v1.2.3")

        context = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=True,
            dry_run=False,
        )

        assert context.version == version
        assert context.previous_version == previous_version
        assert context.branch == branch
        assert context.tag == tag
        assert context.branch_exists is True
        assert context.dry_run is False

    def test_init_when_dry_run_then_stored(self) -> None:
        version = ReleaseVersion(1, 0, 0)
        previous_version = ReleaseVersion(0, 9, 9)
        branch = ReleaseBranchName("release/v1.0.0")
        tag = TagName("v1.0.0")

        context = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=True,
        )

        assert context.dry_run is True
        assert context.branch_exists is False

    def test_init_when_branch_exists_then_flag_true(self) -> None:
        version = ReleaseVersion(2, 0, 0)
        previous_version = ReleaseVersion(1, 9, 9)
        branch = ReleaseBranchName("release/v2.0.0")
        tag = TagName("v2.0.0")

        context = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=True,
            dry_run=False,
        )

        assert context.branch_exists is True

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        version = ReleaseVersion(1, 0, 0)
        previous_version = ReleaseVersion(0, 9, 9)
        branch = ReleaseBranchName("release/v1.0.0")
        tag = TagName("v1.0.0")

        context = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=False,
        )

        with pytest.raises(FrozenInstanceError):
            context.dry_run = True  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        version = ReleaseVersion(1, 0, 0)
        previous_version = ReleaseVersion(0, 9, 9)
        branch = ReleaseBranchName("release/v1.0.0")
        tag = TagName("v1.0.0")

        ctx1 = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=False,
        )
        ctx2 = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=False,
        )

        assert ctx1 == ctx2

    def test_eq_when_different_dry_run_then_not_equal(self) -> None:
        version = ReleaseVersion(1, 0, 0)
        previous_version = ReleaseVersion(0, 9, 9)
        branch = ReleaseBranchName("release/v1.0.0")
        tag = TagName("v1.0.0")

        ctx1 = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=False,
        )
        ctx2 = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=True,
        )

        assert ctx1 != ctx2

    def test_hash_when_same_values_then_same_hash(self) -> None:
        version = ReleaseVersion(1, 0, 0)
        previous_version = ReleaseVersion(0, 9, 9)
        branch = ReleaseBranchName("release/v1.0.0")
        tag = TagName("v1.0.0")

        ctx1 = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=False,
        )
        ctx2 = ReleaseContext(
            version=version,
            previous_version=previous_version,
            branch=branch,
            tag=tag,
            branch_exists=False,
            dry_run=False,
        )

        assert hash(ctx1) == hash(ctx2)
