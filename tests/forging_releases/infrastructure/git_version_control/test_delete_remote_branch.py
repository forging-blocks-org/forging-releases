# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from pathlib import Path

import pytest

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.git_version_control import GitVersionControl


@pytest.mark.integration
class TestDeleteRemoteBranch:
    def test_when_branch_exists_on_remote_then_removes_it(
        self, git_repo_with_remote: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=git_repo_with_remote)
        vc.create_branch(branch_name)
        (Path(git_repo_with_remote) / "pyproject.toml").write_text(
            '[project]\nname = "test"\nversion = "1.2.3"\n'
        )
        vc.commit_release_artifacts()
        vc.push(branch_name)
        assert vc.remote_branch_exists(branch_name) is True
        vc.delete_remote_branch(branch_name)
        assert vc.remote_branch_exists(branch_name) is False

    def test_when_branch_does_not_exist_then_does_not_raise(
        self, git_repo_with_remote: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=git_repo_with_remote)
        vc.delete_remote_branch(branch_name)
