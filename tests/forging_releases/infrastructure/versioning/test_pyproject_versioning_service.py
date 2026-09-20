from __future__ import annotations

from pathlib import Path

import pytest
from forging_releases.domain.errors import InvalidReleaseVersionError
from forging_releases.domain.value_objects import ReleaseLevel, ReleaseVersion
from forging_releases.infrastructure.versioning.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.unit
class TestPyProjectVersioningService:
    def test_current_version_reads_pep621_project_version(self, tmp_path: Path) -> None:
        project_file = tmp_path / "pyproject.toml"
        project_file.write_text('[project]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8")

        service = PyProjectVersioningService(project_file)

        assert service.current_version() == ReleaseVersion(1, 2, 3)

    @pytest.mark.parametrize(
        ("content", "expected_context"),
        [
            ('[tool.poetry]\nversion = "1.2.3"\n', "project.version"),
            ('[project]\nname = "demo"\n', "project.version"),
            ('[project]\nname = "demo"\nversion = 123\n', "project.version"),
            ('[project]\nname = "demo"\nversion = "1.2"\n', "1.2"),
        ],
    )
    def test_current_version_rejects_invalid_pep621_metadata(
        self,
        tmp_path: Path,
        content: str,
        expected_context: str,
    ) -> None:
        project_file = tmp_path / "pyproject.toml"
        project_file.write_text(content, encoding="utf-8")

        with pytest.raises(InvalidReleaseVersionError, match=expected_context):
            PyProjectVersioningService(project_file).current_version()

    def test_apply_version_preserves_unrelated_toml(self, tmp_path: Path) -> None:
        project_file = tmp_path / "pyproject.toml"
        project_file.write_text(
            '# Keep this comment\n'
            '[project]\n'
            'name = "demo"\n'
            'version = "1.2.3"\n'
            '\n'
            '[tool.custom]\n'
            'enabled = true\n',
            encoding="utf-8",
        )
        service = PyProjectVersioningService(project_file)

        service.apply_version(ReleaseVersion(2, 0, 0))

        content = project_file.read_text(encoding="utf-8")
        assert 'version = "2.0.0"' in content
        assert '# Keep this comment' in content
        assert '[tool.custom]\nenabled = true' in content

    def test_apply_version_dry_run_does_not_mutate_file(self, tmp_path: Path) -> None:
        project_file = tmp_path / "pyproject.toml"
        original = '[project]\nname = "demo"\nversion = "1.2.3"\n'
        project_file.write_text(original, encoding="utf-8")
        service = PyProjectVersioningService(project_file)

        service.apply_version(ReleaseVersion(2, 0, 0), dry_run=True)

        assert project_file.read_text(encoding="utf-8") == original

    def test_apply_version_dry_run_validates_existing_metadata(self, tmp_path: Path) -> None:
        project_file = tmp_path / "pyproject.toml"
        project_file.write_text('[project]\nname = "demo"\nversion = "1.2"\n', encoding="utf-8")

        with pytest.raises(InvalidReleaseVersionError, match="project.version"):
            PyProjectVersioningService(project_file).apply_version(
                ReleaseVersion(2, 0, 0), dry_run=True
            )

    def test_compute_next_version_uses_requested_release_level(self, tmp_path: Path) -> None:
        project_file = tmp_path / "pyproject.toml"
        project_file.write_text('[project]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8")
        service = PyProjectVersioningService(project_file)

        assert service.compute_next_version(ReleaseLevel.from_str("minor")) == ReleaseVersion(1, 3, 0)
