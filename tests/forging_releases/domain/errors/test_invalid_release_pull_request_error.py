# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest
from forging_blocks.foundation import ValidationError

from forging_releases.domain.errors import InvalidReleasePullRequestError


@pytest.mark.unit
class TestInvalidReleasePullRequestError:
    @pytest.mark.parametrize(
        "reason",
        [
            pytest.param("missing head branch", id="missing_head"),
            pytest.param("invalid base branch", id="invalid_base"),
            pytest.param("title is required", id="missing_title"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, reason: str) -> None:
        error = InvalidReleasePullRequestError(reason)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "reason",
        [
            pytest.param("missing head branch", id="missing_head"),
            pytest.param("invalid base branch", id="invalid_base"),
            pytest.param("title is required", id="missing_title"),
        ],
    )
    def test_when_created_then_message_contains_reason(self, reason: str) -> None:
        error = InvalidReleasePullRequestError(reason)

        assert reason in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleasePullRequestError("missing head branch")

        result = str(error)

        assert "missing head branch" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleasePullRequestError("missing head branch")

        result = repr(error)

        assert "InvalidReleasePullRequestError" in result
        assert "missing head branch" in result
