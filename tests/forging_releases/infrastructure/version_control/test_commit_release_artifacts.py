# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from pathlib import Path

import pytest
from .conftest import run_git

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.version_control.version_control import GitVersionControl


@pytest.mark.integration
class TestCommitReleaseArtifacts:
    def test_when_changes_exist_then_commits_them(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        (Path(temp_git_repo) / "CHANGELOG.md").write_text("# Changelog\n")
        vc.commit_release_artifacts()
        result = run_git(["git", "log", "-1", "--pretty=%s"], temp_git_repo)
        assert "chore: release" in result.stdout

    def test_when_dry_run_then_no_commit(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        commits_before = len(
            run_git(["git", "log", "--oneline"], temp_git_repo).stdout.strip().splitlines()
        )
        (Path(temp_git_repo) / "CHANGELOG.md").write_text("# Changelog\n")
        vc.commit_release_artifacts(dry_run=True)
        commits_after = len(
            run_git(["git", "log", "--oneline"], temp_git_repo).stdout.strip().splitlines()
        )
        assert commits_after == commits_before
