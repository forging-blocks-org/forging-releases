# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import os
import subprocess


def _make_isolated_env(cwd: str) -> dict[str, str]:
    return {
        **os.environ,
        "HOME": cwd,
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def run_git(cmd: list[str], cwd: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
        env=_make_isolated_env(cwd),
    )


def current_branch(repo_dir: str) -> str:
    result = run_git(["git", "branch", "--show-current"], repo_dir)
    return result.stdout.strip()


def local_branches(repo_dir: str) -> list[str]:
    result = run_git(["git", "branch"], repo_dir)
    return [b.strip().lstrip("* ") for b in result.stdout.strip().splitlines()]
