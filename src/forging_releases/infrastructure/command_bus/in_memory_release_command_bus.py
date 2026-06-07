from __future__ import annotations

from typing import TypeVar

from forging_blocks.application.ports.inbound.message_handler import CommandHandler
from forging_blocks.foundation.messages.command import Command

from forging_releases.application.ports.outbound.release_command_bus import ReleaseCommandBus

T = TypeVar("T", bound=Command[object])

"""In-memory command bus for dispatching release commands."""


class InMemoryReleaseCommandBus(ReleaseCommandBus[T]):
    """An in-memory implementation of ReleaseCommandBus."""

    def __init__(self) -> None:
        """Initialize the bus with an empty handler registry."""
        self._handlers: dict[type[Command[object]], CommandHandler[T]] = {}

    async def register(
        self,
        command_type: type[Command[object]],
        handler: CommandHandler[T],
    ) -> None:
        """Register a handler for a command type.

        Args:
            command_type: The command class to register a handler for.
            handler: The handler to invoke when the command is sent.
        """
        self._handlers[command_type] = handler

    async def send(self, message: T) -> None:
        """Send a command to its registered handler.

        Args:
            message: The command to dispatch.
        """
        handler = self._handlers.get(type(message))
        if handler is not None:
            await handler.handle(message)

    async def dispatch(self, message: T) -> None:
        """Alias for send. Dispatches a command to its registered handler.

        Args:
            message: The command to dispatch.
        """
        await self.send(message)
