from __future__ import annotations

from typing import Self

from forging_releases.application.ports.outbound.release_transaction import ReleaseTransaction
from forging_releases.application.workflow import ReleaseStep

"""In-memory release transaction with step registration and rollback support."""


class InMemoryReleaseTransaction(ReleaseTransaction):
    """Tracks release steps in memory for commit or rollback."""

    def __init__(self) -> None:
        """Initialize with an empty step list."""
        self._steps: list[ReleaseStep] = []

    def register_step(self, step: ReleaseStep) -> None:
        """Register a release step for commit/rollback tracking.

        Args:
            step: The release step to register.
        """
        self._steps.append(step)

    async def commit(self) -> None:
        """Commit the transaction. No-op in this in-memory implementation."""

    async def rollback(self) -> None:
        """Rollback all registered steps in reverse order."""
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
