from __future__ import annotations

from typing import Protocol

from forging_blocks.application.ports.inbound.message_handler import CommandHandler
from forging_blocks.foundation.messages.command import Command

from forging_releases.application.ports.outbound.release_command_bus import ReleaseCommandBus


class _Handler(Protocol):
    async def handle(self, message: Command[object]) -> None: ...


class InMemoryReleaseCommandBus(ReleaseCommandBus[Command[object]]):
    def __init__(self) -> None:
        self._handlers: dict[type[Command[object]], _Handler] = {}

    async def register(
        self,
        command_type: type[Command[object]],
        handler: CommandHandler[Command[object]],
    ) -> None:
        self._handlers[command_type] = handler  # type: ignore[assignment]

    async def send(self, message: Command[object]) -> None:
        handler = self._handlers.get(type(message))
        if handler is not None:
            await handler.handle(message)

    async def dispatch(self, message: Command[object]) -> None:
        await self.send(message)
