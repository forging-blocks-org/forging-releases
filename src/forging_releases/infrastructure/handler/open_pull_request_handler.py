from __future__ import annotations

from forging_releases.application.ports.inbound import (
    OpenReleasePullRequestInput,
    OpenReleasePullRequestUseCase,
)
from forging_releases.domain.commands import OpenPullRequestCommand

"""Command handler that delegates OpenPullRequestCommand to the use case."""


class OpenPullRequestHandler:
    """Handles OpenPullRequestCommand by invoking the OpenReleasePullRequestUseCase."""

    def __init__(self, *, use_case: OpenReleasePullRequestUseCase) -> None:
        """Initialize the handler.

        Args:
            use_case: The use case to delegate to.
        """
        self._use_case = use_case

    async def handle(self, message: OpenPullRequestCommand) -> None:
        """Handle an OpenPullRequestCommand.

        Args:
            message: The command containing version, branch, and dry_run details.
        """
        input_dto = OpenReleasePullRequestInput(
            version=message.version,
            branch=message.branch,
            dry_run=message.dry_run,
        )
        await self._use_case.execute(input_dto)
