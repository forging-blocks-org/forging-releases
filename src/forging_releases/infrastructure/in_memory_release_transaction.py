"""In-memory implementation of the ReleaseTransaction outbound port."""

from __future__ import annotations

from typing import Self

from forging_releases.application.ports.outbound.release_transaction import ReleaseTransaction
from forging_releases.application.workflow import ReleaseStep


class InMemoryReleaseTransaction(ReleaseTransaction):
    """Coordinates commit/rollback of release preparation steps.

    Guarantees:
    - rollback on any exception
    - reverse-order compensation (LIFO)
    """

    def __init__(self) -> None:
        self._steps: list[ReleaseStep] = []

    def register_step(self, step: ReleaseStep) -> None:
        """Register a step with its undo action."""
        self._steps.append(step)

    async def commit(self) -> None:
        """Commit the transaction (no-op in memory)."""

    async def rollback(self) -> None:
        """Rollback the transaction by executing undo actions in reverse."""
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
