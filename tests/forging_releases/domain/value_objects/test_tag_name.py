# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import Ok
from forging_blocks.foundation.errors.cant_modify_immutable_attribute_error import (
    CantModifyImmutableAttributeError,
)

from forging_releases.domain.errors import InvalidTagNameError
from forging_releases.domain.value_objects import ReleaseVersion, TagName


@pytest.mark.unit
class TestTagName:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("1.2.3", id="missing_prefix"),
            pytest.param("version/1.2.3", id="wrong_prefix"),
            pytest.param("v", id="prefix_only"),
            pytest.param("", id="empty_string"),
            pytest.param("V1.2.3", id="uppercase_v"),
            pytest.param(" v1.2.3", id="leading_space"),
            pytest.param("tags/v1.2.3", id="tags_prefix"),
            pytest.param("release/v1.2.3", id="release_prefix"),
            pytest.param("1.2.3v", id="suffix_v"),
            pytest.param("v1.2.3 extra", id="trailing_content"),
        ],
    )
    def test_from_str_when_invalid_prefix_then_err(self, value: str) -> None:
        result = TagName.from_str(value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidTagNameError)
        assert value in result.error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("v1.2", id="too_few_parts"),
            pytest.param("v1.2.3.4", id="too_many_parts"),
            pytest.param("v", id="prefix_only_no_dots"),
            pytest.param("v1", id="single_component"),
            pytest.param("v1.2.3.4.5", id="five_parts"),
            pytest.param("v.", id="trailing_dot"),
            pytest.param("v..", id="double_dot"),
            pytest.param("v.1.2", id="leading_dot_after_prefix"),
        ],
    )
    def test_from_str_when_invalid_structure_then_err(self, value: str) -> None:
        result = TagName.from_str(value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidTagNameError)
        assert value in result.error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("v1.-2.3", id="negative_minor"),
            pytest.param("v1.a.3", id="non_numeric"),
            pytest.param("v-1.2.3", id="negative_major"),
            pytest.param("v1.2.-3", id="negative_patch"),
            pytest.param("v1.2.x", id="non_numeric_patch"),
            pytest.param("vabc.def.ghi", id="all_non_numeric"),
        ],
    )
    def test_from_str_when_invalid_version_then_err(self, value: str) -> None:
        result = TagName.from_str(value)

        assert result.is_err is True
        assert isinstance(result.error, InvalidTagNameError)
        assert value in result.error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("v1.2.3", id="standard"),
            pytest.param("v0.0.0", id="all_zeros"),
            pytest.param("v999.999.999", id="large_components"),
            pytest.param("v1.0.0", id="only_major"),
            pytest.param("v0.1.0", id="only_minor"),
            pytest.param("v0.0.1", id="only_patch"),
        ],
    )
    def test_from_str_when_valid_then_ok(self, value: str) -> None:
        result = TagName.from_str(value)

        assert result == Ok(TagName(value))

    @pytest.mark.parametrize(
        "version, expected",
        [
            pytest.param(ReleaseVersion(1, 2, 3), "v1.2.3", id="standard"),
            pytest.param(ReleaseVersion(0, 0, 0), "v0.0.0", id="all_zeros"),
            pytest.param(ReleaseVersion(999, 999, 999), "v999.999.999", id="large_components"),
            pytest.param(ReleaseVersion(1, 0, 0), "v1.0.0", id="only_major"),
            pytest.param(ReleaseVersion(0, 1, 0), "v0.1.0", id="only_minor"),
            pytest.param(ReleaseVersion(0, 0, 1), "v0.0.1", id="only_patch"),
        ],
    )
    def test_create_when_valid_version_then_returns_tag(
        self, version: ReleaseVersion, expected: str
    ) -> None:
        tag = TagName.create(version)

        assert tag.value == expected

    def test_equality_when_same_value_then_equal(self) -> None:
        assert TagName("v2.0.0") == TagName("v2.0.0")

    def test_equality_when_different_value_then_not_equal(self) -> None:
        assert TagName("v1.0.0") != TagName("v2.0.0")

    def test_equality_when_different_type_then_not_equal(self) -> None:
        assert TagName("v1.0.0") != "v1.0.0"

    def test_hash_when_same_value_then_same_hash(self) -> None:
        assert hash(TagName("v1.0.0")) == hash(TagName("v1.0.0"))

    def test_hash_when_different_value_then_different_hash(self) -> None:
        assert hash(TagName("v1.0.0")) != hash(TagName("v2.0.0"))

    def test_str_when_called_then_returns_representation(self) -> None:
        tag = TagName("v1.0.0")

        assert str(tag) == "TagName('v1.0.0')"

    def test_repr_when_called_then_returns_representation(self) -> None:
        tag = TagName("v1.0.0")

        assert repr(tag) == "TagName('v1.0.0')"

    def test_setattr_when_frozen_then_raises(self) -> None:
        tag = TagName("v1.2.3")

        with pytest.raises(CantModifyImmutableAttributeError):
            tag._value = "v9.9.9"  # type: ignore
