# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import os
import subprocess
from pathlib import Path

import pytest

from forging_releases.application.ports.outbound.changelog_generator import ChangelogRequest
from forging_releases.infrastructure.git_changelog_generator import GitChangelogGenerator


def _isolated_env(cwd: str) -> dict[str, str]:
    return {
        **os.environ,
        "HOME": cwd,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@test.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@test.com",
    }


def _run(cmd: list[str], cwd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, check=check, env=_isolated_env(cwd)
    )


def _make_commit(repo_dir: str, message: str) -> None:
    (Path(repo_dir) / "file.txt").write_text(message)
    _run(["git", "add", "."], repo_dir)
    _run(["git", "commit", "--no-verify", "-m", message], repo_dir)


def _make_tag(repo_dir: str, tag: str) -> None:
    _run(["git", "tag", tag], repo_dir)


@pytest.mark.integration
class TestGitChangelogGenerator:
    async def test_when_commits_exist_after_tag_then_returns_entries(
        self, temp_git_repo: str
    ) -> None:
        _make_commit(temp_git_repo, "feat: add login")
        _make_commit(temp_git_repo, "fix: resolve bug")
        _make_tag(temp_git_repo, "v1.0.0")
        _make_commit(temp_git_repo, "feat: add dashboard")
        _make_commit(temp_git_repo, "fix: patch security")

        gen = GitChangelogGenerator(cwd=temp_git_repo)
        request = ChangelogRequest(from_version="1.0.0")
        response = await gen.generate(request)

        assert len(response.entries) == 2
        assert "- feat: add dashboard" in response.entries
        assert "- fix: patch security" in response.entries

    async def test_when_no_tag_found_then_returns_empty(self, temp_git_repo: str) -> None:
        gen = GitChangelogGenerator(cwd=temp_git_repo)
        request = ChangelogRequest(from_version="99.99.99")
        response = await gen.generate(request)

        assert response.entries == []

    async def test_when_dry_run_then_returns_placeholder(self, temp_git_repo: str) -> None:
        gen = GitChangelogGenerator(cwd=temp_git_repo)
        request = ChangelogRequest(from_version="1.0.0", dry_run=True)
        response = await gen.generate(request)

        assert response.entries == ["[dry-run] changelog entry"]
