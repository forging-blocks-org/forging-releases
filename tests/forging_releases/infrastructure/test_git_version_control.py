# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
"""Integration tests for GitVersionControl."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.git_version_control import GitVersionControl


def _run(cmd: list[str], cwd: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def _current_branch(repo_dir: str) -> str:
    result = _run(["git", "branch", "--show-current"], repo_dir)
    return result.stdout.strip()


def _local_branches(repo_dir: str) -> list[str]:
    result = _run(["git", "branch"], repo_dir)
    return [b.strip().lstrip("* ") for b in result.stdout.strip().splitlines()]


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


@pytest.mark.integration
class TestCreateBranch:
    def test_when_created_then_branch_exists_and_is_checked_out(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        assert _current_branch(temp_git_repo) == branch_name.value
        assert branch_name.value in _local_branches(temp_git_repo)

    def test_when_dry_run_then_branch_is_not_created(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name, dry_run=True)
        assert branch_name.value not in _local_branches(temp_git_repo)
        assert _current_branch(temp_git_repo) == "main"


@pytest.mark.integration
class TestCheckout:
    def test_when_branch_exists_then_switches_to_it(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        vc.checkout(branch_name)
        assert _current_branch(temp_git_repo) == branch_name.value

    def test_when_dry_run_then_does_not_switch(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        vc.checkout(branch_name, dry_run=True)
        assert _current_branch(temp_git_repo) == "main"

    def test_when_branch_does_not_exist_then_raises(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        with pytest.raises(subprocess.CalledProcessError):
            vc.checkout(branch_name)


@pytest.mark.integration
class TestCheckoutMain:
    def test_when_called_then_returns_to_main(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        assert _current_branch(temp_git_repo) == "main"

    def test_when_custom_main_branch_then_returns_to_configured_branch(
        self, temp_git_repo: str
    ) -> None:
        _run(["git", "branch", "-m", "main", "trunk"], temp_git_repo)
        _run(["git", "checkout", "-b", "other"], temp_git_repo)
        vc = GitVersionControl(cwd=temp_git_repo, main_branch="trunk")
        vc.checkout_main()
        assert _current_branch(temp_git_repo) == "trunk"


@pytest.mark.integration
class TestCommitReleaseArtifacts:
    def test_when_changes_exist_then_commits_them(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        (Path(temp_git_repo) / "CHANGELOG.md").write_text("# Changelog\n")
        vc.commit_release_artifacts()
        result = _run(["git", "log", "-1", "--pretty=%s"], temp_git_repo)
        assert "chore: release" in result.stdout

    def test_when_dry_run_then_no_commit(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        commits_before = len(
            _run(["git", "log", "--oneline"], temp_git_repo).stdout.strip().splitlines()
        )
        (Path(temp_git_repo) / "CHANGELOG.md").write_text("# Changelog\n")
        vc.commit_release_artifacts(dry_run=True)
        commits_after = len(
            _run(["git", "log", "--oneline"], temp_git_repo).stdout.strip().splitlines()
        )
        assert commits_after == commits_before


@pytest.mark.integration
class TestDeleteLocalBranch:
    def test_when_branch_exists_then_removes_it(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.create_branch(branch_name)
        vc.checkout_main()
        vc.delete_local_branch(branch_name)
        assert branch_name.value not in _local_branches(temp_git_repo)

    def test_when_branch_does_not_exist_then_does_not_raise(
        self, temp_git_repo: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=temp_git_repo)
        vc.delete_local_branch(branch_name)


@pytest.mark.integration
class TestPush:
    def test_when_pushed_then_branch_exists_on_remote(
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

    def test_when_dry_run_then_no_push(
        self, git_repo_with_remote: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=git_repo_with_remote)
        vc.create_branch(branch_name)
        vc.push(branch_name, dry_run=True)
        assert vc.remote_branch_exists(branch_name) is False


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


@pytest.mark.integration
class TestRemoteBranchExists:
    def test_when_branch_pushed_then_returns_true(
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

    def test_when_branch_not_pushed_then_returns_false(
        self, git_repo_with_remote: str, branch_name: ReleaseBranchName
    ) -> None:
        vc = GitVersionControl(cwd=git_repo_with_remote)
        assert vc.remote_branch_exists(branch_name) is False
