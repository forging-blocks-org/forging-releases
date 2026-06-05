# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import ValidationError

from forging_releases.domain.errors import InvalidTagNameError


@pytest.mark.unit
class TestInvalidTagNameError:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("not-a-tag", id="with_hyphens"),
            pytest.param("release-v1.0", id="branch_name"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, value: str) -> None:
        error = InvalidTagNameError(value)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("not-a-tag", id="with_hyphens"),
            pytest.param("release-v1.0", id="branch_name"),
        ],
    )
    def test_when_created_then_message_contains_input(self, value: str) -> None:
        error = InvalidTagNameError(value)

        assert value in error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("not-a-tag", id="with_hyphens"),
            pytest.param("release-v1.0", id="branch_name"),
        ],
    )
    def test_when_created_then_message_mentions_v_prefix(self, value: str) -> None:
        error = InvalidTagNameError(value)

        assert "v<version>" in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidTagNameError("bad")

        result = str(error)

        assert "bad" in result
        assert "v<version>" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidTagNameError("bad")

        result = repr(error)

        assert "InvalidTagNameError" in result
        assert "bad" in result
