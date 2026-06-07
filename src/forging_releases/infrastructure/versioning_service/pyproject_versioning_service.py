from __future__ import annotations

import re
from pathlib import Path

from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import VersionNotFoundError
from forging_releases.application.ports.outbound.versioning_service import VersioningService
from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion


class PyProjectVersioningService(VersioningService):
    _VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None) -> None:
        self._cwd = cwd

    def current_version(self) -> Result[ReleaseVersion, VersionNotFoundError]:
        content = self._read_pyproject()

        match = self._VERSION_PATTERN.search(content)
        if not match:
            return Err(VersionNotFoundError("version key not found in pyproject.toml"))

        version_str = match.group(1)
        result = ReleaseVersion.from_str(version_str)
        if result.is_err:
            return Err(VersionNotFoundError(f"invalid version in pyproject.toml: {version_str}"))

        release_version = result.value
        assert release_version is not None
        return Ok(release_version)

    def compute_next_version(self, level: ReleaseLevel) -> ReleaseVersion:
        version_result = self.current_version()
        match version_result:
            case Err():
                return ReleaseVersion(0, 1, 0)
            case Ok(value=current):
                pass
            case _:
                return ReleaseVersion(0, 1, 0)

        current = version_result.value
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
            return ""
        return match.group(1)
