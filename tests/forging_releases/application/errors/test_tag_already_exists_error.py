# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError

from forging_releases.application.errors import TagAlreadyExistsError


@pytest.mark.unit
class TestTagAlreadyExistsError:
    def test_when_created_then_is_rule_violation_error(self) -> None:
        error = TagAlreadyExistsError("v1.0.0")

        assert isinstance(error, RuleViolationError)

    @pytest.mark.parametrize(
        "tag_name",
        [
            pytest.param("v1.0.0", id="standard"),
            pytest.param("v0.1.0", id="minor"),
            pytest.param("v99.99.99", id="large"),
        ],
    )
    def test_when_created_then_message_contains_tag_name(self, tag_name: str) -> None:
        error = TagAlreadyExistsError(tag_name)

        assert tag_name in error.message.value
        assert "already exists" in error.message.value

    def test_when_created_then_is_catchable_as_rule_violation(self) -> None:
        with pytest.raises(RuleViolationError):
            raise TagAlreadyExistsError("v1.0.0")

    def test_str_when_called_then_returns_representation(self) -> None:
        error = TagAlreadyExistsError("v1.0.0")

        result = str(error)

        assert "v1.0.0" in result
        assert "already exists" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = TagAlreadyExistsError("v1.0.0")

        result = repr(error)

        assert "TagAlreadyExistsError" in result
        assert "v1.0.0" in result
