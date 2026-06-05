# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import Ok
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
            pytest.param("", id="empty_string"),
            pytest.param("release/v", id="prefix_only"),
            pytest.param("Release/v1.2.3", id="uppercase_release"),
            pytest.param(" release/v1.2.3", id="leading_space"),
            pytest.param("release/v-1.2.3", id="negative_major"),
            pytest.param("release/v1.2.-3", id="negative_patch"),
            pytest.param("release/v1.2.3.4.5", id="five_parts"),
            pytest.param("release/", id="prefix_slash_only"),
            pytest.param("release/vabc", id="non_numeric_after_prefix"),
            pytest.param("rel/v1.2.3", id="abbreviated_prefix"),
        ],
    )
    def test_from_str_when_invalid_value_then_err(self, value: str) -> None:
        result = ReleaseBranchName.from_str(value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidReleaseBranchNameError)
        assert value in result.error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("release/v1.2.3", id="standard"),
            pytest.param("release/v0.0.0", id="all_zeros"),
            pytest.param("release/v999.999.999", id="large_components"),
            pytest.param("release/v1.0.0", id="only_major"),
            pytest.param("release/v0.1.0", id="only_minor"),
            pytest.param("release/v0.0.1", id="only_patch"),
        ],
    )
    def test_from_str_when_valid_then_ok(self, value: str) -> None:
        result = ReleaseBranchName.from_str(value)

        assert result == Ok(ReleaseBranchName(value))

    @pytest.mark.parametrize(
        "version, expected",
        [
            pytest.param(ReleaseVersion(1, 2, 3), "release/v1.2.3", id="standard"),
            pytest.param(ReleaseVersion(0, 0, 0), "release/v0.0.0", id="all_zeros"),
            pytest.param(
                ReleaseVersion(999, 999, 999),
                "release/v999.999.999",
                id="large_components",
            ),
            pytest.param(ReleaseVersion(1, 0, 0), "release/v1.0.0", id="only_major"),
            pytest.param(ReleaseVersion(0, 1, 0), "release/v0.1.0", id="only_minor"),
            pytest.param(ReleaseVersion(0, 0, 1), "release/v0.0.1", id="only_patch"),
        ],
    )
    def test_create_when_valid_version_then_returns_branch(
        self, version: ReleaseVersion, expected: str
    ) -> None:
        branch = ReleaseBranchName.create(version)

        assert branch.value == expected

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

    def test_setattr_when_frozen_then_raises(self) -> None:
        branch = ReleaseBranchName("release/v1.0.0")

        with pytest.raises(CantModifyImmutableAttributeError):
            branch._value = "release/v9.9.9"  # type: ignore
