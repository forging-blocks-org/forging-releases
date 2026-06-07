from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from .conftest import read_version

from forging_blocks.foundation import Ok

from forging_releases.application.errors import VersionNotFoundError
from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestPyProjectVersioningService:
    def test_current_version_when_pyproject_exists_then_reads_version(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)

        result = svc.current_version()

        assert result.is_ok is True
        assert result.value == ReleaseVersion(1, 2, 3)
        assert result.value is not None
        assert result.value.value == "1.2.3"

    @pytest.mark.parametrize(
        "content,substring",
        [
            ('[project]\nname = "test"\n', "version key not found"),
            ('[project]\nversion = "not.a.version"\n', "invalid version"),
            ('[tool]\nkey = "value"\n', "version key not found"),
        ],
    )
    def test_current_version_when_invalid_pyproject_then_returns_err(
        self, content: str, substring: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(content)

            svc = PyProjectVersioningService(cwd=tmpdir)

            result = svc.current_version()

            assert result.is_err is True
            assert isinstance(result.error, VersionNotFoundError)
            assert substring in result.error.message.value

    @pytest.mark.parametrize(
        "level,expected",
        [
            (ReleaseLevel(ReleaseLevelEnum.MAJOR), ReleaseVersion(2, 0, 0)),
            (ReleaseLevel(ReleaseLevelEnum.MINOR), ReleaseVersion(1, 3, 0)),
            (ReleaseLevel(ReleaseLevelEnum.PATCH), ReleaseVersion(1, 2, 4)),
        ],
    )
    def test_compute_next_version_when_level_then_bumps_correctly(
        self, temp_pyproject_dir: str, level: ReleaseLevel, expected: ReleaseVersion
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)

        result = svc.compute_next_version(level)

        assert result.is_ok is True
        assert result.value == expected

    def test_apply_version_when_applied_then_pyproject_updated(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        new_version = ReleaseVersion(2, 0, 0)

        result = svc.apply_version(new_version)

        assert result.is_ok is True
        assert read_version(str(Path(temp_pyproject_dir) / "pyproject.toml")) == "2.0.0"

    def test_apply_version_when_dry_run_then_pyproject_not_modified(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        new_version = ReleaseVersion(9, 9, 9)

        result = svc.apply_version(new_version, dry_run=True)

        assert result.is_ok is True
        assert read_version(str(Path(temp_pyproject_dir) / "pyproject.toml")) == "1.2.3"

    def test_apply_version_when_applied_multiple_times_then_correct_version(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)

        result_a = svc.apply_version(ReleaseVersion(2, 0, 0))
        assert result_a.is_ok is True
        result_b = svc.apply_version(ReleaseVersion(2, 1, 0))
        assert result_b.is_ok is True

        assert svc.current_version() == Ok(ReleaseVersion(2, 1, 0))

    def test_rollback_version_when_rolled_back_then_restores_previous(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)

        result = svc.current_version()
        assert result.is_ok is True
        assert result.value is not None
        original = result.value

        apply_result = svc.apply_version(ReleaseVersion(5, 0, 0))
        assert apply_result.is_ok is True
        rollback_result = svc.rollback_version(original)
        assert rollback_result.is_ok is True

        final_result = svc.current_version()
        assert final_result == Ok(original)
        assert final_result.value is not None
        assert final_result.value.value == "1.2.3"
