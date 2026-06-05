# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError

from forging_releases.application.errors import InvalidVersionError


@pytest.mark.unit
class TestInvalidVersionError:
    def test_init_when_created_then_is_rule_violation_error(self) -> None:
        error = InvalidVersionError("bad.version")

        assert isinstance(error, RuleViolationError)

    @pytest.mark.parametrize(
        "version",
        [
            pytest.param("abc", id="non_numeric"),
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("1.2.3.4", id="too_many_parts"),
            pytest.param("v1.2.3", id="with_prefix"),
        ],
    )
    def test_init_when_created_then_message_contains_version(self, version: str) -> None:
        error = InvalidVersionError(version)

        assert version in error.message.value
        assert "Invalid version format" in error.message.value

    def test_init_when_created_then_is_catchable_as_rule_violation(self) -> None:
        with pytest.raises(RuleViolationError):
            raise InvalidVersionError("bad")

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidVersionError("bad.version")

        result = str(error)

        assert "Invalid version format" in result
        assert "bad.version" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidVersionError("bad.version")

        result = repr(error)

        assert "InvalidVersionError" in result
        assert "bad.version" in result
