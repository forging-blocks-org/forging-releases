# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false, reportReturnType=false, reportInvalidTypeForm=false

"""Shared fixtures for infrastructure test packages."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

def _run_git(cmd: list[str], cwd: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command in the given working directory.

    Args:
        cmd: The git command and arguments.
        cwd: Working directory for the command.
        check: Whether to raise on non-zero exit codes.

    Returns:
        The completed process result.
    """
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)

@pytest.fixture
def temp_git_repo(tmp_path: Path) -> str:
    """Create a temporary git repository for infrastructure tests.

    Initializes a git repo, configures user identity for test commits,
    creates an initial commit, and yields the directory path.
    """
    repo_dir = Path(tempfile.mkdtemp(dir=tmp_path))
    _run_git(["git", "init"], str(repo_dir))
    _run_git(["git", "config", "user.name", "test"], str(repo_dir))
    _run_git(["git", "config", "user.email", "test@test.com"], str(repo_dir))
    _run_git(["git", "commit", "--allow-empty", "-m", "init"], str(repo_dir))
    yield str(repo_dir)


@pytest.fixture
def branch_name():
    """A synthetic release branch name for testing."""
    from forging_releases.domain.value_objects import ReleaseBranchName as _RBN
    return _RBN("release/v1.0.0")
