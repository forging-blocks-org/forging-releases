# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest
from forging_blocks.foundation import ValidationError

from forging_releases.domain.errors import InvalidReleaseLevelError


@pytest.mark.unit
class TestInvalidReleaseLevelError:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("hotfix", id="hotfix_not_supported"),
            pytest.param("pre-release", id="pre_release_not_supported"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, value: str) -> None:
        error = InvalidReleaseLevelError(value)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("hotfix", id="hotfix_not_supported"),
            pytest.param("pre-release", id="pre_release_not_supported"),
        ],
    )
    def test_when_created_then_message_contains_input(self, value: str) -> None:
        error = InvalidReleaseLevelError(value)

        assert value in error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("hotfix", id="hotfix_not_supported"),
            pytest.param("pre-release", id="pre_release_not_supported"),
        ],
    )
    def test_when_created_then_message_lists_allowed_values(self, value: str) -> None:
        error = InvalidReleaseLevelError(value)

        assert "patch" in error.message.value
        assert "minor" in error.message.value
        assert "major" in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseLevelError("bad")

        result = str(error)

        assert "bad" in result
        assert "patch" in result
        assert "minor" in result
        assert "major" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseLevelError("bad")

        result = repr(error)

        assert "InvalidReleaseLevelError" in result
        assert "bad" in result
