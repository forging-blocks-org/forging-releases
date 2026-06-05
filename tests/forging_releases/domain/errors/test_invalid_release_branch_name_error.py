# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest
from forging_blocks.foundation import ValidationError

from forging_releases.domain.errors import InvalidReleaseBranchNameError


@pytest.mark.unit
class TestInvalidReleaseBranchNameError:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("feature/v1.0", id="feature_branch"),
            pytest.param("main", id="main_branch"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, value: str) -> None:
        error = InvalidReleaseBranchNameError(value)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("feature/v1.0", id="feature_branch"),
            pytest.param("main", id="main_branch"),
        ],
    )
    def test_when_created_then_message_contains_input(self, value: str) -> None:
        error = InvalidReleaseBranchNameError(value)

        assert value in error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("feature/v1.0", id="feature_branch"),
            pytest.param("main", id="main_branch"),
        ],
    )
    def test_when_created_then_message_mentions_expected_format(self, value: str) -> None:
        error = InvalidReleaseBranchNameError(value)

        assert "release/v<version>" in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseBranchNameError("bad")

        result = str(error)

        assert "bad" in result
        assert "release/v<version>" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseBranchNameError("bad")

        result = repr(error)

        assert "InvalidReleaseBranchNameError" in result
        assert "bad" in result
