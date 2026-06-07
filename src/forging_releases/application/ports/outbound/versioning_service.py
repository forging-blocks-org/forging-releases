"""Defines the outbound port for computing and applying semantic versions to the project."""

from abc import abstractmethod

from forging_blocks.foundation import Result
from forging_blocks.foundation.ports import OutputPort

from forging_releases.application.errors import VersionNotFoundError
from forging_releases.domain.value_objects import (
    ReleaseLevel,
    ReleaseVersion,
)


class VersioningService(OutputPort):
    """Computes and applies semantic versions to the package definition.

    Must be non-interactive and deterministic.
    """

    @abstractmethod
    def current_version(self) -> Result[ReleaseVersion, VersionNotFoundError]:
        """Read the currently configured version (e.g., from pyproject.toml via Poetry).

        Returns:
            Ok(ReleaseVersion) if the version is found and valid,
            Err(VersionNotFoundError) if the version cannot be determined.
        """
        ...

    @abstractmethod
    def compute_next_version(
        self,
        level: ReleaseLevel,
    ) -> ReleaseVersion:
        """Compute the next version without mutating state."""
        ...

    @abstractmethod
    def apply_version(
        self,
        version: ReleaseVersion,
        *,
        dry_run: bool = False,
    ) -> None:
        """Mutate version to the given target."""
        ...

    @abstractmethod
    def rollback_version(
        self,
        previous: ReleaseVersion,
    ) -> None:
        """Restore the previously captured version.
        Typically implemented as apply_version(previous).
        """
        ...
