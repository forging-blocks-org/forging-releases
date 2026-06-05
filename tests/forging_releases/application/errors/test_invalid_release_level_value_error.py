# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError

from forging_releases.application.errors import InvalidReleaseLevelValueError


@pytest.mark.unit
class TestInvalidReleaseLevelValueError:
    def test_init_when_created_then_is_rule_violation_error(self) -> None:
        error = InvalidReleaseLevelValueError("mega")

        assert isinstance(error, RuleViolationError)

    @pytest.mark.parametrize(
        "level",
        [
            pytest.param("mega", id="invalid_word"),
            pytest.param("micro", id="another_invalid"),
            pytest.param("", id="empty"),
            pytest.param("123", id="numeric"),
        ],
    )
    def test_init_when_created_then_message_contains_level(self, level: str) -> None:
        error = InvalidReleaseLevelValueError(level)

        assert level in error.message.value
        assert "Invalid release level" in error.message.value

    def test_init_when_created_then_is_catchable_as_rule_violation(self) -> None:
        with pytest.raises(RuleViolationError):
            raise InvalidReleaseLevelValueError("bad")

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseLevelValueError("mega")

        result = str(error)

        assert "Invalid release level" in result
        assert "mega" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseLevelValueError("mega")

        result = repr(error)

        assert "InvalidReleaseLevelValueError" in result
        assert "mega" in result
