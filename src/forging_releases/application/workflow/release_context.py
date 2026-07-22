from dataclasses import dataclass

from forging_releases.domain.value_objects import (
    ReleaseBranchName,
    ReleaseVersion,
    TagName,
)


@dataclass(frozen=True)
class ReleaseContext:
    version: ReleaseVersion
    previous_version: ReleaseVersion
    branch: ReleaseBranchName
    tag: TagName
    branch_exists: bool
    dry_run: bool
