# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_releases.application.errors import ReleaseBranchExistsError


@pytest.mark.unit
class TestReleaseBranchExistsError:
    @pytest.mark.parametrize(
        "branch_name",
        [
            pytest.param("release/v1.0.0", id="standard"),
            pytest.param("release/v0.1.0", id="minor"),
            pytest.param("release/v99.99.99", id="large"),
        ],
    )
    def test_init_when_created_then_stores_branch_name(self, branch_name: str) -> None:
        error = ReleaseBranchExistsError(branch_name)

        assert error.branch_name == branch_name

    def test_init_when_created_then_is_exception(self) -> None:
        error = ReleaseBranchExistsError("release/v1.0.0")

        assert isinstance(error, Exception)

    def test_init_when_created_then_is_catchable(self) -> None:
        with pytest.raises(ReleaseBranchExistsError):
            raise ReleaseBranchExistsError("release/v1.0.0")

    def test_str_when_called_then_contains_branch_name(self) -> None:
        error = ReleaseBranchExistsError("release/v2.0.0")

        result = str(error)

        assert "release/v2.0.0" in result
        assert "already exists" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = ReleaseBranchExistsError("release/v2.0.0")

        result = repr(error)

        assert "ReleaseBranchExistsError" in result
