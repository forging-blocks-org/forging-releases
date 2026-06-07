from __future__ import annotations

from forging_releases.application.ports.inbound import (
    OpenReleasePullRequestInput,
    OpenReleasePullRequestUseCase,
)
from forging_releases.domain.commands import OpenPullRequestCommand


class OpenPullRequestHandler:
    def __init__(self, *, use_case: OpenReleasePullRequestUseCase) -> None:
        self._use_case = use_case

    async def handle(self, message: OpenPullRequestCommand) -> None:
        input_dto = OpenReleasePullRequestInput(
            version=message.version,
            branch=message.branch,
            dry_run=message.dry_run,
        )
        result = await self._use_case.execute(input_dto)
        if result.is_err:
            error = result.error
            assert error is not None
            raise RuntimeError(str(error.message.value))
