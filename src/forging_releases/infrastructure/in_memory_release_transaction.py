from __future__ import annotations

from typing import Self

from forging_releases.application.ports.outbound.release_transaction import ReleaseTransaction
from forging_releases.application.workflow import ReleaseStep


class InMemoryReleaseTransaction(ReleaseTransaction):
    def __init__(self) -> None:
        self._steps: list[ReleaseStep] = []

    def register_step(self, step: ReleaseStep) -> None:
        self._steps.append(step)

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        for step in reversed(self._steps):
            step.undo()

    async def __aenter__(self) -> Self:
        self._steps.clear()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
