from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_installed_wheel_help_and_configured_dry_run(tmp_path: Path) -> None:
    """Exercise the published wheel from an isolated venv and fixture repository."""
    missing = [command for command in ("uv", "python3.14", "git", "git-cliff") if shutil.which(command) is None]
    if missing:
        pytest.skip(f"installed-package smoke prerequisites unavailable: {', '.join(missing)}")

    package_root = Path(__file__).resolve().parents[2]
    build_dir = tmp_path / "wheel"
    build_dir.mkdir()
    environment = _clean_environment()

    _run_checked(
        ["uv", "build", "--out-dir", str(build_dir)],
        cwd=package_root,
        env=environment,
    )
    wheels = sorted(build_dir.glob("forging_releases-*.whl"))
    assert len(wheels) == 1, f"expected one forging-releases wheel, found {wheels}"

    venv_dir = build_dir / "venv"
    _run_checked(["python3.14", "-m", "venv", str(venv_dir)], env=environment)
    python = venv_dir / "bin" / "python"
    pip = venv_dir / "bin" / "pip"
    executable = venv_dir / "bin" / "forging-releases"

    _run_checked([str(pip), "install", str(wheels[0])], env=environment)

    for command in (
        [str(executable), "--help"],
        [str(python), "-m", "forging_releases.presentation", "--help"],
    ):
        result = _run_checked(command, env=environment)
        assert "usage:" in result.stdout
        assert "--project-file" in result.stdout

    fixture = _create_fixture_repository(tmp_path / "fixture")
    project_file = fixture / "config" / "project.toml"
    changelog_file = fixture / "docs" / "HISTORY.md"
    before = _repository_state(fixture)
    original_project = project_file.read_text(encoding="utf-8")
    original_changelog = changelog_file.read_text(encoding="utf-8")

    result = _run_checked(
        [
            str(executable),
            "minor",
            "--project-file",
            "config/project.toml",
            "--changelog-file",
            "docs/HISTORY.md",
            "--cliff-config-file",
            "release/cliff.toml",
            "--base-branch",
            "trunk",
            "--remote",
            "upstream",
            "--release-branch-prefix",
            "publish/",
        ],
        cwd=fixture,
        env=environment,
    )

    assert "Version:    0.1.0" in result.stdout
    assert "[DRY-RUN] No changes applied." in result.stdout
    assert project_file.read_text(encoding="utf-8") == original_project
    assert changelog_file.read_text(encoding="utf-8") == original_changelog
    assert _repository_state(fixture) == before


def _clean_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for name in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    ):
        environment.pop(name, None)
    for name in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
        environment.pop(name, None)
    return environment


def _run_checked(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    effective_env = _clean_environment() if env is None else env
    return subprocess.run(
        command,
        cwd=cwd,
        env=effective_env,
        check=True,
        capture_output=True,
        text=True,
    )


def _create_fixture_repository(path: Path) -> Path:
    (path / "config").mkdir(parents=True)
    (path / "docs").mkdir()
    (path / "release").mkdir()
    _run_checked(["git", "init", "-b", "trunk", str(path)], env=_clean_environment())
    _run_checked(["git", "config", "user.name", "Smoke Test"], cwd=path)
    _run_checked(["git", "config", "user.email", "smoke@example.invalid"], cwd=path)

    (path / "config" / "project.toml").write_text(
        """[project]\nname = \"fixture-project\"\nversion = \"0.0.0\"\ndescription = \"Installed smoke fixture\"\nrequires-python = \">=3.14\"\n""",
        encoding="utf-8",
    )
    (path / "docs" / "HISTORY.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n- Existing fixture entry\n",
        encoding="utf-8",
    )
    (path / "release" / "cliff.toml").write_text(
        """[git]\nconventional_commits = true\nfilter_unconventional = true\ncommit_parsers = [{ message = \"^feat\", group = \"Features\" }]\n\n[changelog]\noutput = \"-\"\nbody = \"\"\"\n{% for group, commits in commits | group_by(attribute=\"group\") %}\n### {{ group }}\n{% for commit in commits %}\n- {{ commit.message }}\n{% endfor %}\n{% endfor %}\n\"\"\"\n""",
        encoding="utf-8",
    )
    (path / "README.md").write_text("# Fixture\n", encoding="utf-8")
    _run_checked(["git", "add", "."], cwd=path)
    _run_checked(["git", "commit", "-m", "feat: create smoke fixture"], cwd=path)

    remote = path.parent / "upstream.git"
    _run_checked(["git", "init", "--bare", str(remote)], env=_clean_environment())
    _run_checked(["git", "remote", "add", "upstream", str(remote)], cwd=path)
    _run_checked(["git", "push", "--set-upstream", "upstream", "trunk"], cwd=path)
    return path


def _repository_state(path: Path) -> tuple[str, str, str]:
    branches = _run_checked(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], cwd=path
    ).stdout
    tags = _run_checked(["git", "tag", "--list"], cwd=path).stdout
    remote_branches = _run_checked(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes"], cwd=path
    ).stdout
    return branches, tags, remote_branches
