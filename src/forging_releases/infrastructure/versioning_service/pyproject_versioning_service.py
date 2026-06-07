"""Versioning service backed by a pyproject.toml file."""

from __future__ import annotations

import re
from pathlib import Path

from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import ProjectConfigurationError, VersionNotFoundError
from forging_releases.application.ports.outbound.versioning_service import (
    VersioningService,
    VersioningServiceError,
)
from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion


class PyProjectVersioningService(VersioningService):
    """Reads and updates the project version from pyproject.toml."""

    _VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None) -> None:
        """Initialize the service.

        Args:
            cwd: Working directory containing pyproject.toml. Defaults to current directory.
        """
        self._cwd = cwd

    def current_version(
        self,
    ) -> Result[ReleaseVersion, VersionNotFoundError | ProjectConfigurationError]:
        """Read the current version from pyproject.toml.

        Returns:
            Ok(ReleaseVersion) if the version is found and valid,
            Err(VersionNotFoundError) if the version string is missing or malformed,
            Err(ProjectConfigurationError) if the file cannot be read.
        """
        content: str = ""
        match self._read_pyproject():
            case Err(error=err):
                return Err(err)
            case Ok(value=value):
                content = value
            case _:
                pass

        match self._extract_version(content):
            case Err(error=err):
                return Err(err)
            case Ok(value=version_str):
                pass
            case _:
                return Err(VersionNotFoundError("unknown error extracting version"))

        match ReleaseVersion.from_str(version_str):
            case Err():
                return Err(
                    VersionNotFoundError(f"invalid version in pyproject.toml: {version_str}")
                )
            case Ok(value=release_version):
                return Ok(release_version)
            case _:
                return Err(
                    VersionNotFoundError(f"invalid version in pyproject.toml: {version_str}")
                )

    def compute_next_version(
        self,
        level: ReleaseLevel,
    ) -> Result[ReleaseVersion, VersioningServiceError]:
        """Compute the next version based on the release level.

        Args:
            level: The release level (major, minor, or patch).

        Returns:
            Ok(ReleaseVersion) with the computed next version,
            Err if the current version cannot be read.
        """
        match self.current_version():
            case Err(error=err):
                return Err(err)
            case Ok(value=current):
                match level.value:
                    case ReleaseLevelEnum.MAJOR:
                        return Ok(ReleaseVersion(current.major + 1, 0, 0))
                    case ReleaseLevelEnum.MINOR:
                        return Ok(ReleaseVersion(current.major, current.minor + 1, 0))
                    case ReleaseLevelEnum.PATCH:
                        return Ok(ReleaseVersion(current.major, current.minor, current.patch + 1))
                    case _:
                        return Err(VersionNotFoundError("invalid release level"))
            case _:
                return Err(VersionNotFoundError("unknown error"))

    def apply_version(
        self,
        version: ReleaseVersion,
        *,
        dry_run: bool = False,
    ) -> Result[None, ProjectConfigurationError]:
        """Write the given version into pyproject.toml.

        Args:
            version: The version to apply.
            dry_run: If True, only log the intended change without writing.

        Returns:
            Ok(None) on success,
            Err(ProjectConfigurationError) if the file cannot be read or written.
        """
        if dry_run:
            print(f"{self._DRY_RUN_PREFIX} set version = {version.value}")
            return Ok(None)

        new_content: str = ""
        match self._read_pyproject():
            case Err(error=err):
                return Err(err)
            case Ok(value=content):
                new_content = self._VERSION_PATTERN.sub(f'version = "{version.value}"', content)
            case _:
                pass

        pyproject = self._pyproject_path()
        try:
            pyproject.write_text(new_content)
        except OSError as exc:
            return Err(ProjectConfigurationError("write", str(pyproject), str(exc)))

        return Ok(None)

    def rollback_version(
        self,
        previous: ReleaseVersion,
    ) -> Result[None, ProjectConfigurationError]:
        """Revert to a previous version by re-applying it.

        Args:
            previous: The version to restore.

        Returns:
            Ok(None) on success,
            Err(ProjectConfigurationError) if the file cannot be read or written.
        """
        return self.apply_version(previous)

    def _read_pyproject(self) -> Result[str, ProjectConfigurationError]:
        try:
            return Ok(self._pyproject_path().read_text())
        except OSError as exc:
            return Err(ProjectConfigurationError("read", str(self._pyproject_path()), str(exc)))

    def _pyproject_path(self) -> Path:
        return Path(self._cwd or ".") / "pyproject.toml"

    @classmethod
    def _extract_version(cls, content: str) -> Result[str, VersionNotFoundError]:
        match cls._VERSION_PATTERN.search(content):
            case None:
                return Err(VersionNotFoundError("version key not found in pyproject.toml"))
            case m:
                return Ok(m.group(1))
