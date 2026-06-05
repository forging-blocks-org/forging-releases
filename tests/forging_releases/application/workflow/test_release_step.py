# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
from dataclasses import FrozenInstanceError

import pytest

from forging_releases.application.workflow import ReleaseStep


@pytest.mark.unit
class TestReleaseStep:
    def test_init_when_created_then_stores_name_and_undo(self) -> None:
        called_with: list[str] = []

        def undo_func() -> None:
            called_with.append("undo_called")

        step = ReleaseStep(name="test_step", undo=undo_func)

        assert step.name == "test_step"
        assert step.undo is undo_func

    def test_undo_when_called_then_invokes_callable(self) -> None:
        called_with: list[str] = []

        def undo_func() -> None:
            called_with.append("undo_called")

        step = ReleaseStep(name="checkout_main", undo=undo_func)

        step.undo()

        assert called_with == ["undo_called"]

    def test_undo_when_is_lambda_then_works(self) -> None:
        side_effect: list[str] = []
        step = ReleaseStep(
            name="delete_branch",
            undo=lambda: side_effect.append("deleted"),
        )

        step.undo()

        assert side_effect == ["deleted"]

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        def undo_func() -> None:
            pass

        step = ReleaseStep(name="test", undo=undo_func)

        with pytest.raises(FrozenInstanceError):
            step.name = "changed"  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        def undo_func() -> None:
            pass

        step1 = ReleaseStep(name="step_a", undo=undo_func)
        step2 = ReleaseStep(name="step_a", undo=undo_func)

        assert step1 == step2

    def test_eq_when_different_name_then_not_equal(self) -> None:
        def undo_func() -> None:
            pass

        step1 = ReleaseStep(name="step_a", undo=undo_func)
        step2 = ReleaseStep(name="step_b", undo=undo_func)

        assert step1 != step2

    def test_hash_when_same_values_then_same_hash(self) -> None:
        def undo_func() -> None:
            pass

        step1 = ReleaseStep(name="step", undo=undo_func)
        step2 = ReleaseStep(name="step", undo=undo_func)

        assert hash(step1) == hash(step2)
