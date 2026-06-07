from __future__ import annotations

from typing import TypeVar

from forging_blocks.application.ports.inbound.message_handler import CommandHandler
from forging_blocks.foundation.messages.command import Command

from forging_releases.application.ports.outbound.release_command_bus import ReleaseCommandBus

T = TypeVar("T", bound=Command[object])


class InMemoryReleaseCommandBus(ReleaseCommandBus[T]):
    def __init__(self) -> None:
        self._handlers: dict[type[Command[object]], CommandHandler[T]] = {}

    async def register(
        self,
        command_type: type[Command[object]],
        handler: CommandHandler[T],
    ) -> None:
        self._handlers[command_type] = handler

    async def send(self, message: T) -> None:
        handler = self._handlers.get(type(message))
        if handler is not None:
            await handler.handle(message)

    async def dispatch(self, message: T) -> None:
        await self.send(message)
