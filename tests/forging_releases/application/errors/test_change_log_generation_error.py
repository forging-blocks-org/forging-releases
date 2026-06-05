# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError

from forging_releases.application.errors import ChangelogGenerationError


@pytest.mark.unit
class TestChangelogGenerationError:
    def test_init_when_created_then_is_rule_violation_error(self) -> None:
        error = ChangelogGenerationError("something went wrong")

        assert isinstance(error, RuleViolationError)

    @pytest.mark.parametrize(
        "details",
        [
            pytest.param("network timeout", id="network_timeout"),
            pytest.param("no commits found", id="no_commits"),
            pytest.param("invalid range", id="invalid_range"),
        ],
    )
    def test_init_when_created_then_message_contains_details(self, details: str) -> None:
        error = ChangelogGenerationError(details)

        assert details in error.message.value
        assert "Changelog generation failed" in error.message.value

    def test_init_when_created_then_is_catchable_as_rule_violation(self) -> None:
        with pytest.raises(RuleViolationError):
            raise ChangelogGenerationError("test")

    def test_str_when_called_then_returns_representation(self) -> None:
        error = ChangelogGenerationError("test reason")

        result = str(error)

        assert "Changelog generation failed" in result
        assert "test reason" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = ChangelogGenerationError("test reason")

        result = repr(error)

        assert "ChangelogGenerationError" in result
        assert "test reason" in result
