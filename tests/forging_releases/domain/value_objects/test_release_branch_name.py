# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest
from forging_blocks.foundation.errors.cant_modify_immutable_attribute_error import (
    CantModifyImmutableAttributeError,
)
from forging_releases.domain.errors.invalid_release_branch_name_error import (
    InvalidReleaseBranchNameError,
)
from forging_releases.domain.value_objects.release_branch_name import ReleaseBranchName
from forging_releases.domain.value_objects.release_version import ReleaseVersion


@pytest.mark.unit
class TestReleaseBranchName:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("feature/v1.2.3", id="invalid_prefix"),
            pytest.param("release/v1.2", id="invalid_structure_too_few"),
            pytest.param("release/v1.2.3.4", id="invalid_structure_too_many"),
            pytest.param("release/v1.-2.3", id="negative_version_component"),
            pytest.param("release/vx.y.z", id="non_numeric_version"),
            pytest.param("release/v1.x.3", id="non_numeric_minor"),
        ],
    )
    def test_init_when_invalid_value_then_error(self, value: str) -> None:
        with pytest.raises(InvalidReleaseBranchNameError):
            ReleaseBranchName(value)

    def test_init_when_valid_value_then_success(self) -> None:
        branch = ReleaseBranchName("release/v1.2.3")

        assert branch.value == "release/v1.2.3"

    def test_value_when_called_then_returns_raw_value(self) -> None:
        branch = ReleaseBranchName("release/v1.0.0")

        assert branch.value == "release/v1.0.0"

    def test_from_version_when_valid_version_then_branch_created(self) -> None:
        version = ReleaseVersion(1, 2, 3)

        branch = ReleaseBranchName.from_version(version)

        assert branch.value == "release/v1.2.3"

    def test_from_version_when_zero_version_then_branch_created(self) -> None:
        version = ReleaseVersion(0, 0, 0)

        branch = ReleaseBranchName.from_version(version)

        assert branch.value == "release/v0.0.0"

    def test_equality_when_same_value_then_equal(self) -> None:
        assert ReleaseBranchName("release/v1.0.0") == ReleaseBranchName(
            "release/v1.0.0"
        )

    def test_equality_when_different_value_then_not_equal(self) -> None:
        assert ReleaseBranchName("release/v1.0.0") != ReleaseBranchName(
            "release/v2.0.0"
        )

    def test_equality_when_different_type_then_not_equal(self) -> None:
        assert ReleaseBranchName("release/v1.0.0") != "release/v1.0.0"

    def test_hash_when_same_value_then_same_hash(self) -> None:
        assert hash(ReleaseBranchName("release/v1.0.0")) == hash(
            ReleaseBranchName("release/v1.0.0")
        )

    def test_hash_when_different_value_then_different_hash(self) -> None:
        assert hash(ReleaseBranchName("release/v1.0.0")) != hash(
            ReleaseBranchName("release/v2.0.0")
        )

    def test_str_when_called_then_returns_representation(self) -> None:
        branch = ReleaseBranchName("release/v1.0.0")

        assert str(branch) == "ReleaseBranchName('release/v1.0.0')"

    def test_repr_when_called_then_returns_representation(self) -> None:
        branch = ReleaseBranchName("release/v1.0.0")

        assert repr(branch) == "ReleaseBranchName('release/v1.0.0')"

    def test_init_when_created_then_cannot_modify_value(self) -> None:
        branch = ReleaseBranchName("release/v1.0.0")

        with pytest.raises(CantModifyImmutableAttributeError):
            branch._value = "release/v9.9.9"  # type: ignore
