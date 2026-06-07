# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from pathlib import Path

import pytest
from ..conftest import _run_git

from forging_releases.application.ports.outbound.changelog_generator import ChangelogRequest
from forging_releases.infrastructure.changelog_generator.git_changelog_generator import (
    GitChangelogGenerator,
)


def _make_commit(repo_dir: str, message: str) -> None:
    (Path(repo_dir) / "file.txt").write_text(message)
    _run_git(["git", "add", "."], repo_dir)
    _run_git(["git", "commit", "--no-verify", "-m", message], repo_dir)


def _make_tag(repo_dir: str, tag: str) -> None:
    _run_git(["git", "tag", tag], repo_dir)


@pytest.mark.integration
class TestGitChangelogGenerator:
    async def test_generate_when_commits_exist_after_tag_then_returns_entries(
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

    async def test_generate_when_no_tag_found_then_returns_empty(self, temp_git_repo: str) -> None:
        gen = GitChangelogGenerator(cwd=temp_git_repo)
        request = ChangelogRequest(from_version="99.99.99")

        response = await gen.generate(request)

        assert response.entries == []

    async def test_generate_when_dry_run_then_returns_placeholder(self, temp_git_repo: str) -> None:
        gen = GitChangelogGenerator(cwd=temp_git_repo)
        request = ChangelogRequest(from_version="1.0.0", dry_run=True)

        response = await gen.generate(request)

        assert response.entries == ["[dry-run] changelog entry"]
