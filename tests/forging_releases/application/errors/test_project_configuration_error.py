# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation.errors.rule_violation_error import RuleViolationError

from forging_releases.application.errors import ProjectConfigurationError


@pytest.mark.unit
class TestProjectConfigurationError:
    def test_init_when_created_then_is_rule_violation_error(self) -> None:
        error = ProjectConfigurationError("read", "/path/to/pyproject.toml", "file not found")

        assert isinstance(error, RuleViolationError)

    def test_init_when_created_then_stores_operation(self) -> None:
        error = ProjectConfigurationError("read", "/path/to/pyproject.toml", "file not found")

        assert error.operation == "read"

    def test_init_when_created_then_stores_path(self) -> None:
        error = ProjectConfigurationError("write", "/some/config.toml", "permission denied")

        assert error.path == "/some/config.toml"

    @pytest.mark.parametrize(
        "operation,path_param,details",
        [
            pytest.param("read", "/a/pyproject.toml", "file not found", id="read_not_found"),
            pytest.param("write", "/b/pyproject.toml", "permission denied", id="write_permission"),
            pytest.param("read", "/c/config.toml", "is a directory", id="read_is_directory"),
        ],
    )
    def test_init_when_created_then_message_contains_elements(
        self, operation: str, path_param: str, details: str
    ) -> None:
        error = ProjectConfigurationError(operation, path_param, details)

        assert "Project configuration" in error.message.value
        assert operation in error.message.value
        assert details in error.message.value
        assert path_param in error.message.value
        assert f"failed: {details}" in error.message.value
        assert f"(path: {path_param})" in error.message.value

    def test_init_when_created_then_is_catchable_as_rule_violation(self) -> None:
        with pytest.raises(RuleViolationError):
            raise ProjectConfigurationError("read", "/path", "test")

    def test_str_when_called_then_returns_representation(self) -> None:
        error = ProjectConfigurationError("read", "/a/b/pyproject.toml", "file not found")

        result = str(error)

        assert "Project configuration read failed" in result
        assert "file not found" in result
        assert "/a/b/pyproject.toml" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = ProjectConfigurationError("write", "/x/y/config.toml", "permission denied")

        result = repr(error)

        assert "ProjectConfigurationError" in result
        assert "write" in result
        assert "permission denied" in result
        assert "/x/y/config.toml" in result
