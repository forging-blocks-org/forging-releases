# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_blocks.foundation import ValidationError

from forging_releases.domain.errors import InvalidReleaseVersionError


@pytest.mark.unit
class TestInvalidReleaseVersionError:
    @pytest.mark.parametrize(
        "release_version",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("v1.2.3", id="semver_with_prefix"),
            pytest.param("", id="empty_string"),
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("a.b.c", id="non_numeric"),
        ],
    )
    def test_when_created_then_is_validation_error(self, release_version: str) -> None:
        error = InvalidReleaseVersionError(release_version)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "release_version",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("v1.2.3", id="semver_with_prefix"),
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("a.b.c", id="non_numeric"),
        ],
    )
    def test_when_created_then_message_contains_input(self, release_version: str) -> None:
        error = InvalidReleaseVersionError(release_version)

        assert release_version in error.message.value

    @pytest.mark.parametrize(
        "release_version",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("v1.2.3", id="semver_with_prefix"),
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("a.b.c", id="non_numeric"),
        ],
    )
    def test_when_created_then_message_expects_semver_format(self, release_version: str) -> None:
        error = InvalidReleaseVersionError(release_version)

        assert "major" in error.message.value
        assert "minor" in error.message.value
        assert "patch" in error.message.value

    @pytest.mark.parametrize(
        "release_version",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("v1.2.3", id="semver_with_prefix"),
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("a.b.c", id="non_numeric"),
        ],
    )
    def test_when_created_then_context_contains_input(self, release_version: str) -> None:
        error = InvalidReleaseVersionError(release_version)

        assert error.context == {"release_version": release_version}

    @pytest.mark.parametrize(
        "release_version",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("v1.2.3", id="semver_with_prefix"),
            pytest.param("1.2", id="too_few_parts"),
            pytest.param("a.b.c", id="non_numeric"),
        ],
    )
    def test_when_created_then_is_catchable_as_validation_error(self, release_version: str) -> None:
        with pytest.raises(ValidationError):
            raise InvalidReleaseVersionError(release_version)

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseVersionError("bad")

        result = str(error)

        assert "bad" in result
        assert "major" in result
        assert "minor" in result
        assert "patch" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseVersionError("bad")

        result = repr(error)

        assert "InvalidReleaseVersionError" in result
        assert "bad" in result
