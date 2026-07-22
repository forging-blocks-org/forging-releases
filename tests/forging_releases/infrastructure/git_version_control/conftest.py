# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import subprocess

from ..conftest import _run_git


def run_git(cmd: list[str], cwd: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run_git(cmd, cwd, check=check)


def current_branch(repo_dir: str) -> str:
    result = run_git(["git", "branch", "--show-current"], repo_dir)
    return result.stdout.strip()


def local_branches(repo_dir: str) -> list[str]:
    result = run_git(["git", "branch"], repo_dir)
    return [b.strip().lstrip("* ") for b in result.stdout.strip().splitlines()]
