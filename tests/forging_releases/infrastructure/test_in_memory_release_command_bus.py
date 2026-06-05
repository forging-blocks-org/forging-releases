# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
"""Integration tests for InMemoryReleaseCommandBus."""

from __future__ import annotations

import pytest

from forging_blocks.application.ports.inbound.message_handler import CommandHandler
from forging_blocks.foundation.messages.command import Command

from forging_releases.infrastructure.in_memory_release_command_bus import (
    InMemoryReleaseCommandBus,
)

type PayloadType = dict[str, str | bool]


class _TestCommand(Command[PayloadType]):
    def __init__(self) -> None:
        self._val: PayloadType = {"key": "value"}
        super().__init__()

    @property
    def value(self) -> PayloadType:
        return self._val

    @property
    def _payload(self) -> PayloadType:
        return self._val


class _TestHandler(CommandHandler[_TestCommand]):
    def __init__(self) -> None:
        self.handled: list[_TestCommand] = []

    async def handle(self, message: _TestCommand) -> None:
        self.handled.append(message)


@pytest.mark.integration
class TestInMemoryReleaseCommandBus:
    async def test_when_handler_registered_then_receives_command(self) -> None:
        bus = InMemoryReleaseCommandBus()
        handler = _TestHandler()
        await bus.register(_TestCommand, handler)  # type: ignore[arg-type]
        cmd = _TestCommand()
        await bus.send(cmd)
        assert len(handler.handled) == 1
        assert handler.handled[0] is cmd

    async def test_when_no_handler_then_silently_ignored(self) -> None:
        bus = InMemoryReleaseCommandBus()
        cmd = _TestCommand()
        await bus.send(cmd)
