from __future__ import annotations

import re
from pathlib import Path

from forging_releases.application.ports.outbound.versioning_service import VersioningService
from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion


class PyProjectVersioningService(VersioningService):
    _VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None) -> None:
        self._cwd = cwd

    def current_version(self) -> ReleaseVersion:
        content = self._read_pyproject()

        match = self._VERSION_PATTERN.search(content)
        if not match:
            raise ValueError("version key not found in project section")

        version_str = match.group(1)
        result = ReleaseVersion.from_str(version_str)
        if result.is_err:
            raise ValueError(f"Invalid version in pyproject.toml: {version_str}")

        release_version = result.value
        assert release_version is not None
        return release_version

    def compute_next_version(self, level: ReleaseLevel) -> ReleaseVersion:
        current = self.current_version()
        match level.value:
            case ReleaseLevelEnum.MAJOR:
                return ReleaseVersion(current.major + 1, 0, 0)
            case ReleaseLevelEnum.MINOR:
                return ReleaseVersion(current.major, current.minor + 1, 0)
            case ReleaseLevelEnum.PATCH:
                return ReleaseVersion(current.major, current.minor, current.patch + 1)

    def apply_version(self, version: ReleaseVersion, *, dry_run: bool = False) -> None:
        if dry_run:
            print(f"{self._DRY_RUN_PREFIX} set version = {version.value}")
            return

        pyproject = self._pyproject_path()
        content = pyproject.read_text()
        new_content = self._VERSION_PATTERN.sub(f'version = "{version.value}"', content)
        pyproject.write_text(new_content)

    def rollback_version(self, previous: ReleaseVersion) -> None:
        self.apply_version(previous)

    def _read_pyproject(self) -> str:
        return self._pyproject_path().read_text()

    def _pyproject_path(self) -> Path:
        return Path(self._cwd or ".") / "pyproject.toml"

    @classmethod
    def _extract_version(cls, content: str) -> str:
        match = cls._VERSION_PATTERN.search(content)
        if not match:
            raise ValueError("version key not found")
        return match.group(1)
