from __future__ import annotations

from pathlib import Path
from typing import cast

import tomlkit

from forging_releases.application.ports.outbound import VersioningService
from forging_releases.domain.value_objects import (
    ReleaseLevel,
    ReleaseVersion,
)


class PyProjectVersioningService(VersioningService):
    """Reads and writes the version in pyproject.toml using tomlkit.

    Uses tomlkit.parse() / tomlkit.dumps() for full comment and formatting
    preservation during round-trip edits.

    Responsibilities:
        - Read current version from [project] version field.
        - Compute semantic version bump (major/minor/patch).
        - Apply version with comment/formatting preservation.
        - Rollback to a previous version.

    Non-Responsibilities:
        - Manage git commits or tags.
        - Validate pyproject.toml schema beyond version presence.
    """

    def __init__(self, pyproject_path: Path) -> None:
        self._pyproject_path = pyproject_path

    def current_version(self) -> ReleaseVersion:
        doc = self._read_doc()
        version_str = cast(str, doc["project"]["version"])  # type: ignore[index]
        return ReleaseVersion.from_str(version_str)

    def compute_next_version(
        self,
        level: ReleaseLevel,
    ) -> ReleaseVersion:
        current = self.current_version()

        if level.value == "major":
            return ReleaseVersion(current.major + 1, 0, 0)

        if level.value == "minor":
            return ReleaseVersion(current.major, current.minor + 1, 0)

        return ReleaseVersion(current.major, current.minor, current.patch + 1)

    def apply_version(
        self,
        version: ReleaseVersion,
        *,
        dry_run: bool = False,
    ) -> None:
        if dry_run:
            return
        doc = self._read_doc()
        doc["project"]["version"] = version.value  # type: ignore[index]
        self._write_doc(doc)

    def rollback_version(
        self,
        previous: ReleaseVersion,
    ) -> None:
        self.apply_version(previous)

    def _read_doc(self) -> tomlkit.TOMLDocument:
        with self._pyproject_path.open("r", encoding="utf-8") as f:
            return tomlkit.parse(f.read())

    def _write_doc(self, doc: tomlkit.TOMLDocument) -> None:
        with self._pyproject_path.open("w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(doc))  # type: ignore[reportUnknownMemberType]
