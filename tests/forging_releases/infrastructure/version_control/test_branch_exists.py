# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.version_control.version_control import GitVersionControl


@pytest.mark.integration
class TestBranchExists:
    def test_when_branch_is_main_then_returns_true(self, temp_git_repo: str) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        result = vc.branch_exists(ReleaseBranchName("main"))
        assert result is True

    def test_when_branch_does_not_exist_then_returns_false(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        result = vc.branch_exists(branch_name)
        assert result is False
