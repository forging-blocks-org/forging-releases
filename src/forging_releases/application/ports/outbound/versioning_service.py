"""Defines the outbound port for computing and applying semantic versions to the project."""

from abc import abstractmethod

from forging_blocks.foundation import Result
from forging_blocks.foundation.ports import OutputPort

from forging_releases.application.errors import ProjectConfigurationError, VersionNotFoundError
from forging_releases.domain.value_objects import (
    ReleaseLevel,
    ReleaseVersion,
)

type VersioningServiceError = VersionNotFoundError | ProjectConfigurationError


class VersioningService(OutputPort):
    """Computes and applies semantic versions to the package definition.

    Must be non-interactive and deterministic.
    """

    @abstractmethod
    def current_version(self) -> Result[ReleaseVersion, VersioningServiceError]:
        """Read the currently configured version.

        Returns:
            Ok(ReleaseVersion) if the version is found and valid,
            Err(VersioningServiceError) if the version cannot be determined.
        """
        ...

    @abstractmethod
    def compute_next_version(
        self,
        level: ReleaseLevel,
    ) -> Result[ReleaseVersion, VersioningServiceError]:
        """Compute the next version without mutating state.

        Returns:
            Ok(ReleaseVersion) with the computed next version,
            Err with VersioningServiceError if the current version cannot be read.
        """
        ...

    @abstractmethod
    def apply_version(
        self,
        version: ReleaseVersion,
        *,
        dry_run: bool = False,
    ) -> Result[None, ProjectConfigurationError]:
        """Mutate version to the given target.

        Returns:
            Ok(None) on success,
            Err(ProjectConfigurationError) if the configuration file cannot be written.
        """
        ...

    @abstractmethod
    def rollback_version(
        self,
        previous: ReleaseVersion,
    ) -> Result[None, ProjectConfigurationError]:
        """Restore the previously captured version.

        Typically implemented as apply_version(previous).

        Returns:
            Ok(None) on success,
            Err(ProjectConfigurationError) if the configuration file cannot be written.
        """
        ...
