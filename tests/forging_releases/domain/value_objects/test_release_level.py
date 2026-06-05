# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import Ok
from forging_blocks.foundation.errors.cant_modify_immutable_attribute_error import (
    CantModifyImmutableAttributeError,
)

from forging_releases.domain.errors.invalid_release_level_error import (
    InvalidReleaseLevelError,
)
from forging_releases.domain.value_objects.release_level import (
    ReleaseLevel,
    ReleaseLevelEnum,
)


@pytest.mark.unit
class TestReleaseLevel:
    @pytest.mark.parametrize(
        "level, expected_value",
        [
            pytest.param(ReleaseLevelEnum.MAJOR, "major", id="major"),
            pytest.param(ReleaseLevelEnum.MINOR, "minor", id="minor"),
            pytest.param(ReleaseLevelEnum.PATCH, "patch", id="patch"),
        ],
    )
    def test_init_when_valid_enum_then_value_is_correct(
        self, level: ReleaseLevelEnum, expected_value: str
    ) -> None:
        release_level = ReleaseLevel(level)

        assert release_level.value == expected_value

    @pytest.mark.parametrize(
        "raw_value, expected_level_value",
        [
            pytest.param("MAJOR", ReleaseLevelEnum.MAJOR, id="uppercase_major"),
            pytest.param("major", ReleaseLevelEnum.MAJOR, id="lowercase_major"),
            pytest.param("Minor", ReleaseLevelEnum.MINOR, id="mixed_case_minor"),
            pytest.param("PATCH", ReleaseLevelEnum.PATCH, id="uppercase_patch"),
            pytest.param("minor", ReleaseLevelEnum.MINOR, id="lowercase_minor"),
            pytest.param("patch", ReleaseLevelEnum.PATCH, id="lowercase_patch"),
            pytest.param("Major", ReleaseLevelEnum.MAJOR, id="title_case_major"),
        ],
    )
    def test_from_str_when_valid_then_creates_level(
        self, raw_value: str, expected_level_value: ReleaseLevelEnum
    ) -> None:
        result = ReleaseLevel.from_str(raw_value)

        assert result.is_ok is True
        assert result == Ok(ReleaseLevel(expected_level_value))

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("hotfix", id="invalid_value"),
            pytest.param("release", id="another_invalid_value"),
            pytest.param("", id="empty_string"),
            pytest.param("MAJORs", id="typo_with_extra_char"),
            pytest.param(" major ", id="whitespace_padded"),
            pytest.param("   ", id="whitespace_only"),
            pytest.param("\t", id="tab_only"),
            pytest.param("\n", id="newline_only"),
            pytest.param("123", id="numeric_string"),
            pytest.param("ma", id="partial_prefix"),
            pytest.param("maj", id="partial_name"),
            pytest.param("patche", id="truncated_name"),
            pytest.param("!@#$%", id="special_characters"),
            pytest.param("MAJOR ", id="trailing_space"),
            pytest.param(" MINOR", id="leading_space"),
        ],
    )
    def test_from_str_when_invalid_then_error(self, raw_value: str) -> None:
        result = ReleaseLevel.from_str(raw_value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidReleaseLevelError)
        assert raw_value in result.error.message.value

    def test_equality_when_same_level_then_equal(self) -> None:
        assert (
            ReleaseLevel.from_str("PATCH").value == ReleaseLevel.from_str("PATCH").value
        )

    def test_equality_when_different_level_then_not_equal(self) -> None:
        assert (
            ReleaseLevel.from_str("PATCH").value != ReleaseLevel.from_str("MINOR").value
        )

    def test_equality_when_different_type_then_not_equal(self) -> None:
        assert ReleaseLevel.from_str("PATCH").value != "patch"

    def test_hash_when_same_value_then_same_hash(self) -> None:
        assert hash(ReleaseLevel.from_str("PATCH").value) == hash(
            ReleaseLevel.from_str("PATCH").value
        )

    def test_hash_when_different_value_then_different_hash(self) -> None:
        assert hash(ReleaseLevel.from_str("PATCH").value) != hash(
            ReleaseLevel.from_str("MINOR").value
        )

    def test_str_when_called_then_returns_representation(self) -> None:
        level = ReleaseLevel.from_str("PATCH").value

        assert str(level) == "ReleaseLevel(<ReleaseLevelEnum.PATCH: 'patch'>)"

    def test_repr_when_called_then_returns_representation(self) -> None:
        level = ReleaseLevel.from_str("PATCH").value

        assert repr(level) == "ReleaseLevel(<ReleaseLevelEnum.PATCH: 'patch'>)"

    def test_setattr_when_frozen_then_raises(self) -> None:
        level = ReleaseLevel.from_str("PATCH").value

        with pytest.raises(CantModifyImmutableAttributeError):
            level._level = ReleaseLevelEnum.MAJOR  # type: ignore
