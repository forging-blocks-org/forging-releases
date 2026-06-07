# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest
from .conftest import current_branch, local_branches

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.version_control.version_control import GitVersionControl


@pytest.mark.integration
class TestCreateBranch:
    def test_when_created_then_branch_exists_and_is_checked_out(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        assert current_branch(temp_git_repo) == branch_name.value
        assert branch_name.value in local_branches(temp_git_repo)

    def test_when_dry_run_then_branch_is_not_created(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name, dry_run=True)
        assert branch_name.value not in local_branches(temp_git_repo)
        assert current_branch(temp_git_repo) == "main"
