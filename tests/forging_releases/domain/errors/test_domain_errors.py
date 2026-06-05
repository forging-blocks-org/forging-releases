# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest
from forging_blocks.foundation import ValidationError

from forging_releases.domain.errors import (
    InvalidReleaseBranchNameError,
    InvalidReleaseLevelError,
    InvalidReleasePullRequestError,
    InvalidReleaseVersionError,
    InvalidTagNameError,
)


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


@pytest.mark.unit
class TestInvalidTagNameError:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("not-a-tag", id="with_hyphens"),
            pytest.param("release-v1.0", id="branch_name"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, value: str) -> None:
        error = InvalidTagNameError(value)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("not-a-tag", id="with_hyphens"),
            pytest.param("release-v1.0", id="branch_name"),
        ],
    )
    def test_when_created_then_message_contains_input(self, value: str) -> None:
        error = InvalidTagNameError(value)

        assert value in error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("not-a-tag", id="with_hyphens"),
            pytest.param("release-v1.0", id="branch_name"),
        ],
    )
    def test_when_created_then_message_mentions_v_prefix(self, value: str) -> None:
        error = InvalidTagNameError(value)

        assert "v<version>" in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidTagNameError("bad")

        result = str(error)

        assert "bad" in result
        assert "v<version>" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidTagNameError("bad")

        result = repr(error)

        assert "InvalidTagNameError" in result
        assert "bad" in result


@pytest.mark.unit
class TestInvalidReleaseLevelError:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("hotfix", id="hotfix_not_supported"),
            pytest.param("pre-release", id="pre_release_not_supported"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, value: str) -> None:
        error = InvalidReleaseLevelError(value)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("hotfix", id="hotfix_not_supported"),
            pytest.param("pre-release", id="pre_release_not_supported"),
        ],
    )
    def test_when_created_then_message_contains_input(self, value: str) -> None:
        error = InvalidReleaseLevelError(value)

        assert value in error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("hotfix", id="hotfix_not_supported"),
            pytest.param("pre-release", id="pre_release_not_supported"),
        ],
    )
    def test_when_created_then_message_lists_allowed_values(self, value: str) -> None:
        error = InvalidReleaseLevelError(value)

        assert "patch" in error.message.value
        assert "minor" in error.message.value
        assert "major" in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseLevelError("bad")

        result = str(error)

        assert "bad" in result
        assert "patch" in result
        assert "minor" in result
        assert "major" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseLevelError("bad")

        result = repr(error)

        assert "InvalidReleaseLevelError" in result
        assert "bad" in result


@pytest.mark.unit
class TestInvalidReleaseBranchNameError:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("feature/v1.0", id="feature_branch"),
            pytest.param("main", id="main_branch"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, value: str) -> None:
        error = InvalidReleaseBranchNameError(value)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("feature/v1.0", id="feature_branch"),
            pytest.param("main", id="main_branch"),
        ],
    )
    def test_when_created_then_message_contains_input(self, value: str) -> None:
        error = InvalidReleaseBranchNameError(value)

        assert value in error.message.value

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("bad", id="simple_invalid"),
            pytest.param("feature/v1.0", id="feature_branch"),
            pytest.param("main", id="main_branch"),
        ],
    )
    def test_when_created_then_message_mentions_expected_format(self, value: str) -> None:
        error = InvalidReleaseBranchNameError(value)

        assert "release/v<version>" in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseBranchNameError("bad")

        result = str(error)

        assert "bad" in result
        assert "release/v<version>" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleaseBranchNameError("bad")

        result = repr(error)

        assert "InvalidReleaseBranchNameError" in result
        assert "bad" in result


@pytest.mark.unit
class TestInvalidReleasePullRequestError:
    @pytest.mark.parametrize(
        "reason",
        [
            pytest.param("missing head branch", id="missing_head"),
            pytest.param("invalid base branch", id="invalid_base"),
            pytest.param("title is required", id="missing_title"),
            pytest.param("", id="empty_string"),
        ],
    )
    def test_when_created_then_is_validation_error(self, reason: str) -> None:
        error = InvalidReleasePullRequestError(reason)

        assert isinstance(error, ValidationError)

    @pytest.mark.parametrize(
        "reason",
        [
            pytest.param("missing head branch", id="missing_head"),
            pytest.param("invalid base branch", id="invalid_base"),
            pytest.param("title is required", id="missing_title"),
        ],
    )
    def test_when_created_then_message_contains_reason(self, reason: str) -> None:
        error = InvalidReleasePullRequestError(reason)

        assert reason in error.message.value

    def test_str_when_called_then_returns_representation(self) -> None:
        error = InvalidReleasePullRequestError("missing head branch")

        result = str(error)

        assert "missing head branch" in result

    def test_repr_when_called_then_returns_representation(self) -> None:
        error = InvalidReleasePullRequestError("missing head branch")

        result = repr(error)

        assert "InvalidReleasePullRequestError" in result
        assert "missing head branch" in result
