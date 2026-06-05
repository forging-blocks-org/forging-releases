# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import Ok
from forging_blocks.foundation.errors.cant_modify_immutable_attribute_error import (
    CantModifyImmutableAttributeError,
)

from forging_releases.domain.errors import InvalidReleaseVersionError
from forging_releases.domain.value_objects.release_version import ReleaseVersion


@pytest.mark.unit
class TestReleaseVersion:
    @pytest.mark.parametrize(
        "major, minor, patch, expected_input",
        [
            pytest.param(1, 1, -1, "1.1.-1", id="negative_patch"),
            pytest.param(1, -1, 1, "1.-1.1", id="negative_minor"),
            pytest.param(-1, 1, 1, "-1.1.1", id="negative_major"),
            pytest.param(0, 0, -1, "0.0.-1", id="negative_patch_zero_others"),
            pytest.param(-1, -1, -1, "-1.-1.-1", id="all_negative"),
            pytest.param(0, -1, 0, "0.-1.0", id="negative_minor_zero_others"),
            pytest.param(-1, 0, 0, "-1.0.0", id="negative_major_zero_others"),
        ],
    )
    def test_create_when_negative_component_then_err(
        self,
        major: int,
        minor: int,
        patch: int,
        expected_input: str,
    ) -> None:
        result = ReleaseVersion.create(major, minor, patch)

        assert result.is_err is True
        assert isinstance(result.error, InvalidReleaseVersionError)
        assert expected_input in result.error.message.value

    @pytest.mark.parametrize(
        "major, minor, patch",
        [
            pytest.param(0, 0, 0, id="all_zeros"),
            pytest.param(0, 4, 2, id="valid_0.4.2"),
            pytest.param(1, 3, 2, id="valid_1.3.2"),
            pytest.param(4, 1, 8, id="valid_4.1.8"),
            pytest.param(99, 99, 99, id="large_values"),
            pytest.param(1, 0, 0, id="only_major"),
            pytest.param(0, 1, 0, id="only_minor"),
            pytest.param(0, 0, 1, id="only_patch"),
            pytest.param(255, 255, 255, id="byte_max_boundary"),
        ],
    )
    def test_create_when_valid_version_then_ok(
        self,
        major: int,
        minor: int,
        patch: int,
    ) -> None:
        result = ReleaseVersion.create(major, minor, patch)

        assert result == Ok(ReleaseVersion(major, minor, patch))

    @pytest.mark.parametrize(
        "raw_value, expected_major, expected_minor, expected_patch",
        [
            pytest.param("1.2.3", 1, 2, 3, id="valid_standard"),
            pytest.param("0.0.0", 0, 0, 0, id="valid_zeros"),
            pytest.param("10.20.30", 10, 20, 30, id="valid_large"),
            pytest.param(" 1.2.3", 1, 2, 3, id="leading_whitespace"),
            pytest.param("1.2.3 ", 1, 2, 3, id="trailing_whitespace"),
            pytest.param(" 1.2.3 ", 1, 2, 3, id="surrounding_whitespace"),
            pytest.param("999.999.999", 999, 999, 999, id="large_components"),
            pytest.param("1.0.0", 1, 0, 0, id="only_major_nonzero"),
            pytest.param("0.1.0", 0, 1, 0, id="only_minor_nonzero"),
            pytest.param("0.0.1", 0, 0, 1, id="only_patch_nonzero"),
        ],
    )
    def test_from_str_when_valid_then_creates_version(
        self,
        raw_value: str,
        expected_major: int,
        expected_minor: int,
        expected_patch: int,
    ) -> None:
        result = ReleaseVersion.from_str(raw_value)

        assert result == Ok(
            ReleaseVersion(expected_major, expected_minor, expected_patch)
        )
        assert result.value is not None
        assert result.value.major == expected_major
        assert result.value.minor == expected_minor
        assert result.value.patch == expected_patch
        assert (
            result.value.value == f"{expected_major}.{expected_minor}.{expected_patch}"
        )

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("1.2.3.4", id="too_many_parts"),
            pytest.param("a.b.c", id="non_numeric"),
            pytest.param("", id="empty_string"),
            pytest.param("1.2.x", id="non_numeric_patch"),
            pytest.param("-1.2.3", id="negative_major"),
            pytest.param("1.-2.3", id="negative_minor"),
            pytest.param("1.2.-3", id="negative_patch"),
            pytest.param("1.2.3.4.5", id="five_parts"),
            pytest.param("1", id="single_number"),
            pytest.param("abc", id="single_non_numeric"),
            pytest.param(".1.2.3", id="leading_dot"),
            pytest.param("1.2.3.", id="trailing_dot"),
            pytest.param("1..3", id="double_dot"),
            pytest.param("   ", id="whitespace_only"),
            pytest.param("\t", id="tab"),
            pytest.param("\n", id="newline"),
        ],
    )
    def test_from_str_when_invalid_then_error(self, raw_value: str) -> None:
        result = ReleaseVersion.from_str(raw_value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidReleaseVersionError)
        assert raw_value in result.error.message.value

    def test_equality_when_same_components_then_equal(self) -> None:
        assert ReleaseVersion(1, 2, 3) == ReleaseVersion(1, 2, 3)

    def test_equality_when_different_components_then_not_equal(self) -> None:
        assert ReleaseVersion(1, 2, 3) != ReleaseVersion(1, 2, 4)

    def test_equality_when_different_type_then_not_equal(self) -> None:
        assert ReleaseVersion(1, 2, 3) != "1.2.3"

    def test_hash_when_same_value_then_same_hash(self) -> None:
        assert hash(ReleaseVersion(1, 2, 3)) == hash(ReleaseVersion(1, 2, 3))

    def test_hash_when_different_value_then_different_hash(self) -> None:
        assert hash(ReleaseVersion(1, 2, 3)) != hash(ReleaseVersion(4, 5, 6))

    def test_str_when_called_then_returns_representation(self) -> None:
        version = ReleaseVersion(1, 2, 3)

        assert str(version) == "ReleaseVersion(1, 2, 3)"

    def test_repr_when_called_then_returns_representation(self) -> None:
        version = ReleaseVersion(1, 2, 3)

        assert repr(version) == "ReleaseVersion(1, 2, 3)"

    def test_setattr_when_frozen_then_raises(self) -> None:
        version = ReleaseVersion(1, 2, 3)

        with pytest.raises(CantModifyImmutableAttributeError):
            version._major = 9  # type: ignore
