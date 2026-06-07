from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from forging_releases.infrastructure.container import Container

_PYPROJECT_TEMPLATE = """[project]
name = "test-project"
version = "0.1.0"
description = "A test project"
requires-python = ">=3.14"
"""


@pytest.fixture
def container_with_temp_repo() -> Generator[Container]:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "repo"
        repo_dir.mkdir()
        _run_git_init(str(repo_dir))
        pyproject = repo_dir / "pyproject.toml"
        pyproject.write_text(_PYPROJECT_TEMPLATE)
        _run_git_commit(str(repo_dir))

        c = Container(
            cwd=str(repo_dir),
            main_branch="main",
            github_owner="test-owner",
            github_repo="test-repo",
            github_token="test-token",
            github_base_url="http://localhost:1",
        )
        yield c


def _run_git_init(repo_dir: str) -> None:
    import os
    import subprocess

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@test.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@test.com",
    })
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=repo_dir,
        env=env,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir,
        env=env,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        env=env,
        capture_output=True,
        check=True,
    )


def _run_git_commit(repo_dir: str) -> None:
    import os
    import subprocess

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@test.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@test.com",
    })
    subprocess.run(
        ["git", "add", "."],
        cwd=repo_dir,
        env=env,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "initial commit"],
        cwd=repo_dir,
        env=env,
        capture_output=True,
        check=True,
    )
