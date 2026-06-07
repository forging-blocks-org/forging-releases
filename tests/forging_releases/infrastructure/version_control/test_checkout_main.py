# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest
from .conftest import current_branch, run_git

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.version_control.git_version_control import GitVersionControl


@pytest.mark.integration
class TestCheckoutMain:
    def test_when_called_then_returns_to_main(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        assert current_branch(temp_git_repo) == "main"

    def test_when_custom_main_branch_then_returns_to_configured_branch(
        self, temp_git_repo: str
    ) -> None:
        run_git(["git", "branch", "-m", "main", "trunk"], temp_git_repo)
        run_git(["git", "checkout", "-b", "other"], temp_git_repo)
        vc = GitVersionControl(cwd=temp_git_repo, main_branch="trunk")
        vc.checkout_main()
        assert current_branch(temp_git_repo) == "trunk"
