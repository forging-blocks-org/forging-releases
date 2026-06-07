"""Defines the inbound port (use case interface) for preparing a release."""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field

from forging_blocks.application.ports import UseCase
from forging_blocks.foundation import Result

from forging_releases.application.errors import (
    CommandExecutionError,
    InvalidReleaseLevelValueError,
    VersionNotFoundError,
)


@dataclass(frozen=True)
class PrepareReleaseInput:
    """Request DTO for preparing a release.

    All values are raw primitives.
    Validation and conversion to Value Objects
    happens inside the use case.

    Future options (intentionally not modeled yet):
    - author: str            # release author / actor
    - dry_run_reason: str    # explanation for dry runs
    - allow_dirty: bool      # allow uncommitted changes
    """

    level: str
    dry_run: bool = False


@dataclass(frozen=True)
class PrepareReleaseOutput:
    """Response DTO for preparing a release.

    Contains only serializable primitives so it can be:
    - printed by the CLI
    - logged
    - consumed by CI steps
    """

    version: str
    branch: str
    tag: str
    changelog_entries: list[str] = field(default_factory=list[str])


type _PrepareReleaseError = (
    InvalidReleaseLevelValueError | VersionNotFoundError | CommandExecutionError
)


class PrepareReleaseUseCase(
    UseCase[PrepareReleaseInput, Result[PrepareReleaseOutput, _PrepareReleaseError]]
):
    """Prepares a release from the main branch.

    Responsibilities:
    - validate release level
    - validate current branch is main
    - compute next version
    - create or resume release branch
    - apply version bump (unless dry_run=True)
    - create git tag (unless dry_run=True)
    - commit and push changes (unless dry_run=True)

    Notes:
    - The use case must remain idempotent
    - Dry runs must never mutate external state
    """

    @abstractmethod
    async def execute(
        self,
        request: PrepareReleaseInput,
    ) -> Result[PrepareReleaseOutput, _PrepareReleaseError]:
        """Execute the release preparation workflow.

        Args:
            request: Input DTO with the release level and dry-run flag.

        Returns:
            Ok with PrepareReleaseOutput on success,
            Err with InvalidReleaseLevelValueError, VersionNotFoundError, or
            CommandExecutionError on failure.
        """
        ...
