# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_releases.application.workflow import ReleaseStep
from forging_releases.infrastructure.release_transaction.in_memory_release_transaction import (
    InMemoryReleaseTransaction,
)


@pytest.mark.integration
class TestInMemoryReleaseTransaction:
    async def test___aexit___when_no_exception_then_no_rollback(self) -> None:
        calls: list[str] = []

        step = ReleaseStep(name="test", undo=lambda: calls.append("rolled_back"))
        tx = InMemoryReleaseTransaction()

        async with tx:
            tx.register_step(step)

        assert calls == []

    async def test___aexit___when_exception_then_rolls_back_in_reverse(self) -> None:
        calls: list[str] = []

        step1 = ReleaseStep(name="first", undo=lambda: calls.append("undo_first"))
        step2 = ReleaseStep(name="second", undo=lambda: calls.append("undo_second"))
        tx = InMemoryReleaseTransaction()

        with pytest.raises(ValueError, match="boom"):
            async with tx:
                tx.register_step(step1)
                tx.register_step(step2)
                raise ValueError("boom")

        assert calls == ["undo_second", "undo_first"]

    async def test___aexit___when_no_steps_registered_then_no_error_on_exception(self) -> None:
        tx = InMemoryReleaseTransaction()

        with pytest.raises(ValueError, match="boom"):
            async with tx:
                raise ValueError("boom")
