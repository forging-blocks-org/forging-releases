# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
"""Integration tests for PyProjectVersioningService."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion
from forging_releases.infrastructure.pyproject_versioning_service import (
    PyProjectVersioningService,
)

_PYPROJECT_TEMPLATE = """[project]
name = "test-project"
version = "1.2.3"
description = "A test project"
requires-python = ">=3.14"
"""


@pytest.fixture
def temp_pyproject_dir() -> Generator[str]:
    """Create a temp directory with a pyproject.toml file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pyproject = Path(tmpdir) / "pyproject.toml"
        pyproject.write_text(_PYPROJECT_TEMPLATE)
        yield tmpdir


def _read_version(pyproject_path: str) -> str:
    content = Path(pyproject_path).read_text()
    return PyProjectVersioningService._extract_version(content)


@pytest.mark.integration
class TestCurrentVersion:
    def test_when_pyproject_exists_then_reads_version(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        version = svc.current_version()
        assert version == ReleaseVersion(1, 2, 3)
        assert version.value == "1.2.3"


@pytest.mark.integration
class TestComputeNextVersion:
    def test_when_major_level_then_bumps_major(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        level = ReleaseLevel(ReleaseLevelEnum.MAJOR)
        next_ver = svc.compute_next_version(level)
        assert next_ver == ReleaseVersion(2, 0, 0)

    def test_when_minor_level_then_bumps_minor(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        level = ReleaseLevel(ReleaseLevelEnum.MINOR)
        next_ver = svc.compute_next_version(level)
        assert next_ver == ReleaseVersion(1, 3, 0)

    def test_when_patch_level_then_bumps_patch(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        level = ReleaseLevel(ReleaseLevelEnum.PATCH)
        next_ver = svc.compute_next_version(level)
        assert next_ver == ReleaseVersion(1, 2, 4)


@pytest.mark.integration
class TestApplyVersion:
    def test_when_applied_then_pyproject_updated(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        new_version = ReleaseVersion(2, 0, 0)
        svc.apply_version(new_version)
        assert _read_version(str(Path(temp_pyproject_dir) / "pyproject.toml")) == "2.0.0"

    def test_when_dry_run_then_pyproject_not_modified(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        new_version = ReleaseVersion(9, 9, 9)
        svc.apply_version(new_version, dry_run=True)
        assert _read_version(str(Path(temp_pyproject_dir) / "pyproject.toml")) == "1.2.3"

    def test_when_applied_multiple_times_then_correct_version(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        svc.apply_version(ReleaseVersion(2, 0, 0))
        svc.apply_version(ReleaseVersion(2, 1, 0))
        assert svc.current_version() == ReleaseVersion(2, 1, 0)


@pytest.mark.integration
class TestRollbackVersion:
    def test_when_rolled_back_then_restores_previous(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        original = svc.current_version()
        svc.apply_version(ReleaseVersion(5, 0, 0))
        svc.rollback_version(original)
        assert svc.current_version() == original
        assert svc.current_version().value == "1.2.3"


@pytest.mark.integration
class TestEdgeCases:
    def test_when_missing_version_key_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            with pytest.raises(ValueError, match="version key not found"):
                svc.current_version()

    def test_when_invalid_version_in_pyproject_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[project]\nversion = "not.a.version"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            with pytest.raises(ValueError, match="Invalid version"):
                svc.current_version()

    def test_when_no_project_section_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[tool]\nkey = "value"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            with pytest.raises(ValueError, match="version key not found"):
                svc.current_version()
