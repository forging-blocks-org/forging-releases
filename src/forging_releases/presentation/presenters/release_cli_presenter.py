"""Presentation workflow for preparing a release."""

from __future__ import annotations

from argparse import Namespace
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import cast

from forging_releases.application.errors.change_log_generation_error import (
    ChangelogGenerationError,
)
from forging_releases.application.errors.pull_request_service_error import PullRequestServiceError
from forging_releases.application.errors.release_branch_exists_error import ReleaseBranchExistsError
from forging_releases.application.errors.tag_already_exists_error import TagAlreadyExistsError
from forging_releases.application.errors.version_control_error import VersionControlError
from forging_releases.application.ports.inbound.prepare_release_use_case import (
    PrepareReleaseInput,
)
from forging_releases.domain.errors.invalid_release_version_error import InvalidReleaseVersionError
from forging_releases.infrastructure.configuration import ReleaseConfiguration
from forging_releases.infrastructure.container import Container
from forging_releases.presentation.parsers import ReleaseCliParser

type ContainerFactory = Callable[[ReleaseConfiguration], Container]

_EXPECTED_ERROR_TYPES: tuple[type[Exception], ...] = (
    VersionControlError,
    PullRequestServiceError,
    TagAlreadyExistsError,
    ReleaseBranchExistsError,
    ChangelogGenerationError,
    InvalidReleaseVersionError,
)


class ReleaseCliPresenter:
    """Coordinate command-line input, release preparation, and user output."""

    def __init__(self, parser: ReleaseCliParser, container_factory: ContainerFactory) -> None:
        self._parser = parser
        self._container_factory = container_factory

    async def present(self, argv: Sequence[str] | None = None) -> None:
        """Prepare a release using parsed options and print its calculated version."""
        parsed = self._parser.parse(argv)
        try:
            configuration = self._configuration_from(parsed)
            container = self._container_factory(configuration)
            await container.initialize()
            prepare_release_use_case = container.get_prepare_release_use_case()
            dry_run = not cast(bool, parsed.execute)
            output = await prepare_release_use_case.execute(
                PrepareReleaseInput(level=cast(str, parsed.level), dry_run=dry_run)
            )
        except _EXPECTED_ERROR_TYPES as error:
            print(str(error))
            raise SystemExit(1) from None

        print(f"Version:    {output.version}")
        if dry_run:
            print("[DRY-RUN] No changes applied. Use --execute to apply.")

    @staticmethod
    def _configuration_from(parsed: Namespace) -> ReleaseConfiguration:
        return ReleaseConfiguration(
            project_file=Path(cast(str | Path, parsed.project_file)),
            changelog_file=Path(cast(str | Path, parsed.changelog_file)),
            cliff_config_file=Path(cast(str | Path, parsed.cliff_config_file)),
            base_branch=cast(str, parsed.base_branch),
            remote=cast(str, parsed.remote),
            release_branch_prefix=cast(str, parsed.release_branch_prefix),
        )
