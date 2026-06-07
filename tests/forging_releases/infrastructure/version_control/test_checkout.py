# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import subprocess

import pytest
from .conftest import current_branch

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.version_control.version_control import GitVersionControl


@pytest.mark.integration
class TestCheckout:
    def test_when_branch_exists_then_switches_to_it(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        vc.checkout(branch_name)
        assert current_branch(temp_git_repo) == branch_name.value

    def test_when_dry_run_then_does_not_switch(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        vc.checkout(branch_name, dry_run=True)
        assert current_branch(temp_git_repo) == "main"

    def test_when_branch_does_not_exist_then_raises(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        with pytest.raises(subprocess.CalledProcessError):
            vc.checkout(branch_name)
