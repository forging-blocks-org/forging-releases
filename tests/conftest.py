"""Shared fixtures for forging-releases tests."""

from pathlib import Path

import pytest

from tests.fixtures.git_cliff_scenarios import (
    Scenario,
    scenario_changelog_with_unreleased,
    scenario_empty_repo,
    scenario_existing_changelog_no_unreleased,
    scenario_repo_with_multiple_tags,
    scenario_repo_with_single_tag,
)
from tests.fixtures.git_test_repository import SANITIZED_ENV, GitTestRepository

__all__ = [
    "SANITIZED_ENV",
    "Scenario",
    "scenario_changelog_with_unreleased",
    "scenario_empty_repo",
    "scenario_existing_changelog_no_unreleased",
    "scenario_repo_with_multiple_tags",
    "scenario_repo_with_single_tag",
    "git_repo",
    "pyproject_toml",
    "git_repo_with_remote",
]


@pytest.fixture
def git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GitTestRepository:
    """Provides a temporary, fully initialised git repository."""
    repo = GitTestRepository.init(tmp_path)
    monkeypatch.chdir(tmp_path)
    return repo


@pytest.fixture
def pyproject_toml(git_repo: GitTestRepository) -> GitTestRepository:
    """Injects a minimal pyproject.toml (version 0.0.0) into the repo and commits it."""
    content = """\
[project]
name = "test-project"
version = "0.0.0"
description = "Test project"
requires-python = ">=3.14"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
    (git_repo.path / "pyproject.toml").write_text(content, encoding="utf-8")
    git_repo.commit("chore: add pyproject.toml")
    return git_repo


@pytest.fixture
def git_repo_with_remote(
    git_repo: GitTestRepository, tmp_path_factory: pytest.TempPathFactory
) -> GitTestRepository:
    """Adds a bare git remote (origin) to the repo and pushes main."""
    import subprocess

    remote_dir = tmp_path_factory.mktemp("remote")
    subprocess.run(
        ["git", "init", "--bare", str(remote_dir / "origin.git")],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "remote", "add", "origin", str(remote_dir / "origin.git")],
        cwd=git_repo.path,
        check=True,
        capture_output=True,
    )
    return git_repo
