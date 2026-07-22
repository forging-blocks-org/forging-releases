from __future__ import annotations

from pathlib import Path
from forging_releases.domain.errors import InvalidReleaseVersionError

from forging_releases.application.ports.outbound.versioning_service import VersioningService
from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion


class PyProjectVersioningService(VersioningService):
    def __init__(self, *, cwd: str | None = None) -> None:
        self._cwd = cwd

    @property
    def _pyproject_path(self) -> Path:
        base = Path(self._cwd) if self._cwd else Path.cwd()
        return base / "pyproject.toml"

    def current_version(self) -> ReleaseVersion:
        content = self._pyproject_path.read_text()
        version_str = self._extract_version(content)
        try:
            return ReleaseVersion.from_str(version_str)
        except InvalidReleaseVersionError:
            raise ValueError(f"Invalid version in pyproject.toml: {version_str}")

    def compute_next_version(self, level: ReleaseLevel) -> ReleaseVersion:
        current = self.current_version()
        match level.value:
            case ReleaseLevelEnum.MAJOR:
                return ReleaseVersion(current.major + 1, 0, 0)
            case ReleaseLevelEnum.MINOR:
                return ReleaseVersion(current.major, current.minor + 1, 0)
            case ReleaseLevelEnum.PATCH:
                return ReleaseVersion(current.major, current.minor, current.patch + 1)
            case _:
                raise ValueError(f"Unknown release level: {level.value}")

    def apply_version(
        self,
        version: ReleaseVersion,
        *,
        dry_run: bool = False,
    ) -> None:
        if dry_run:
            print(f"[dry-run] Would set version to {version.value} in pyproject.toml")
            return
        content = self._pyproject_path.read_text()
        old = self._extract_version(content)
        new_content = content.replace(f'version = "{old}"', f'version = "{version.value}"', 1)
        self._pyproject_path.write_text(new_content)

    def rollback_version(self, previous: ReleaseVersion) -> None:
        self.apply_version(previous, dry_run=False)

    @staticmethod
    def _extract_version(content: str) -> str:
        in_project = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "[project]":
                in_project = True
                continue
            if in_project and stripped.startswith("["):
                in_project = False
                continue
            if in_project and stripped.startswith("version"):
                parts = stripped.split("=", 1)
                if len(parts) == 2:
                    raw = parts[1].strip().strip('"').strip("'")
                    return raw
        raise ValueError("version key not found in [project] section")
