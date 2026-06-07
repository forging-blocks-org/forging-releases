# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest
from .conftest import local_branches

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.version_control.version_control import GitVersionControl


@pytest.mark.integration
class TestDeleteLocalBranch:
    def test_when_branch_exists_then_removes_it(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        vc.delete_local_branch(branch_name)
        assert branch_name.value not in local_branches(temp_git_repo)

    def test_when_branch_does_not_exist_then_does_not_raise(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.delete_local_branch(branch_name)
