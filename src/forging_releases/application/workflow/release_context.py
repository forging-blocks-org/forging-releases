"""Holds the mutable state accumulated during a release preparation workflow."""

from dataclasses import dataclass

from forging_releases.domain.value_objects import (
    ReleaseBranchName,
    ReleaseVersion,
    TagName,
)


@dataclass(frozen=True)
class ReleaseContext:
    """Immutable snapshot of the state for the current release preparation.

    Attributes:
        version: The target release version.
        previous_version: The version before the bump.
        branch: The release branch name.
        tag: The tag name for the release.
        branch_exists: Whether the release branch already exists remotely.
        dry_run: If True, no external state should be mutated.
    """

    version: ReleaseVersion
    previous_version: ReleaseVersion
    branch: ReleaseBranchName
    tag: TagName
    branch_exists: bool
    dry_run: bool
