# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import os
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from forging_releases.domain.value_objects import ReleaseBranchName


def _make_git_env(cwd: str) -> dict[str, str]:
    return {
        **os.environ,
        "HOME": cwd,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Test Runner",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test Runner",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }


def _run(cmd: list[str], cwd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
        env=_make_git_env(cwd),
    )


@pytest.fixture
def temp_git_repo() -> Generator[str]:
    with tempfile.TemporaryDirectory() as base_dir:
        repo_dir = Path(base_dir) / "repo"
        repo_dir.mkdir()
        _run(["git", "init", "-b", "main"], str(repo_dir))
        _run(["git", "config", "user.email", "test@example.com"], str(repo_dir))
        _run(["git", "config", "user.name", "Test User"], str(repo_dir))
        (repo_dir / "README.md").write_text("# Test Repo\n")
        _run(["git", "add", "."], str(repo_dir))
        _run(["git", "commit", "--no-verify", "-m", "initial commit"], str(repo_dir))
        yield str(repo_dir)


@pytest.fixture
def git_repo_with_remote(temp_git_repo: str) -> Generator[str]:
    base = Path(temp_git_repo).parent
    bare_dir = base / "bare.git"
    bare_dir.mkdir()
    _run(["git", "init", "--bare"], str(bare_dir))
    _run(["git", "remote", "add", "origin", str(bare_dir)], temp_git_repo)
    _run(["git", "push", "--set-upstream", "origin", "main"], temp_git_repo)
    yield temp_git_repo


@pytest.fixture
def branch_name() -> ReleaseBranchName:
    return ReleaseBranchName("release/v1.2.3")
