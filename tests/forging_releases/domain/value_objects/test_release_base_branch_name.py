# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import Ok
from forging_blocks.foundation.errors.cant_modify_immutable_attribute_error import (
    CantModifyImmutableAttributeError,
)

from forging_releases.domain.errors.invalid_release_branch_name_error import (
    InvalidReleaseBranchNameError,
)
from forging_releases.domain.value_objects.release_base_branch_name import (
    ReleaseBaseBranchName,
)


@pytest.mark.unit
class TestReleaseBaseBranchName:
    def test_init_when_valid_value_then_success(self) -> None:
        branch = ReleaseBaseBranchName("release/v1.2.3")

        assert branch.value == "release/v1.2.3"

    @pytest.mark.parametrize(
        "value, expected_value",
        [
            pytest.param("release/v0.0.1", "release/v0.0.1", id="standard"),
            pytest.param("release/v1.2.3", "release/v1.2.3", id="typical_version"),
            pytest.param("release/v", "release/v", id="prefix_only"),
            pytest.param(
                "release/v1.2.3-beta+build",
                "release/v1.2.3-beta+build",
                id="semver_with_suffix",
            ),
            pytest.param("release/v999.999.999", "release/v999.999.999", id="large_components"),
        ],
    )
    def test_from_string_when_value_starts_with_release_v_then_ok(
        self, value: str, expected_value: str
    ) -> None:
        result = ReleaseBaseBranchName.from_string(value)

        assert result == Ok(ReleaseBaseBranchName(expected_value))

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("feature/v1.2.3", id="wrong_prefix"),
            pytest.param("release/foo", id="non_version_value"),
            pytest.param("", id="empty_string"),
            pytest.param("main", id="plain_branch"),
            pytest.param("   ", id="whitespace_only"),
            pytest.param(" release/v1.0.0", id="leading_space"),
            pytest.param("develop", id="develop_branch"),
            pytest.param("hotfix/v1.0.0", id="hotfix_prefix"),
            pytest.param("Release/v1.0.0", id="uppercase_release"),
        ],
    )
    def test_from_string_when_value_doesnt_start_with_release_v_then_err(self, value: str) -> None:
        result = ReleaseBaseBranchName.from_string(value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidReleaseBranchNameError)
        assert value in result.error.message.value

    def test_equality_when_same_value_then_equal(self) -> None:
        assert ReleaseBaseBranchName("release/v1.0.0") == ReleaseBaseBranchName("release/v1.0.0")

    def test_equality_when_different_value_then_not_equal(self) -> None:
        assert ReleaseBaseBranchName("release/v1.0.0") != ReleaseBaseBranchName("release/v2.0.0")

    def test_equality_when_different_type_then_not_equal(self) -> None:
        assert ReleaseBaseBranchName("release/v1.0.0") != "release/v1.0.0"

    def test_hash_when_same_value_then_same_hash(self) -> None:
        assert hash(ReleaseBaseBranchName("release/v1.0.0")) == hash(
            ReleaseBaseBranchName("release/v1.0.0")
        )

    def test_hash_when_different_value_then_different_hash(self) -> None:
        assert hash(ReleaseBaseBranchName("release/v1.0.0")) != hash(
            ReleaseBaseBranchName("release/v2.0.0")
        )

    def test_str_when_called_then_returns_representation(self) -> None:
        branch = ReleaseBaseBranchName("release/v1.0.0")

        assert str(branch) == "ReleaseBaseBranchName('release/v1.0.0')"

    def test_repr_when_called_then_returns_representation(self) -> None:
        branch = ReleaseBaseBranchName("release/v1.0.0")

        assert repr(branch) == "ReleaseBaseBranchName('release/v1.0.0')"

    def test_setattr_when_frozen_then_raises(self) -> None:
        branch = ReleaseBaseBranchName("release/v1.0.0")

        with pytest.raises(CantModifyImmutableAttributeError):
            branch._value = "release/v9.9.9"  # type: ignore
