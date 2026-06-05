# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
import pytest

from forging_releases.domain.commands import OpenPullRequestCommand


@pytest.mark.unit
class TestOpenPullRequestCommand:
    def test_init_when_valid_args_then_success(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.2.3",
            branch="release/v1.2.3",
            dry_run=False,
        )

        assert cmd.version == "1.2.3"
        assert cmd.branch == "release/v1.2.3"
        assert cmd.dry_run is False

    def test_init_when_dry_run_is_true_then_success(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=True,
        )

        assert cmd.dry_run is True

    def test_value_when_called_then_returns_payload(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.2.3",
            branch="release/v1.2.3",
            dry_run=False,
        )

        assert cmd.value == {
            "version": "1.2.3",
            "branch": "release/v1.2.3",
            "dry_run": False,
        }

    def test_version_when_called_then_returns_version(self) -> None:
        cmd = OpenPullRequestCommand(
            version="2.0.0",
            branch="release/v2.0.0",
            dry_run=True,
        )

        assert cmd.version == "2.0.0"

    def test_branch_when_called_then_returns_branch(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd.branch == "release/v1.0.0"

    def test_dry_run_when_called_then_returns_dry_run(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=True,
        )

        assert cmd.dry_run is True

    def test_payload_when_called_then_returns_value(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd._payload == cmd.value

    def test_command_id_when_called_then_returns_uuid(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd.command_id == cmd.message_id

    def test_issued_at_when_called_then_returns_created_at(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd.issued_at == cmd.created_at

    def test_message_id_when_called_then_returns_uuid(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd.message_id is not None

    def test_metadata_when_called_then_returns_metadata(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd.metadata is not None
        assert cmd.metadata.message_type == "OpenPullRequestCommand"

    def test_to_dict_when_called_then_returns_dict(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        result = cmd.to_dict()

        assert "metadata" in result
        assert "payload" in result
        assert result["payload"] == {
            "version": "1.0.0",
            "branch": "release/v1.0.0",
            "dry_run": False,
        }

    def test_equality_when_same_id_then_equal(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd == cmd

    def test_equality_when_different_id_then_not_equal(self) -> None:
        cmd1 = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )
        cmd2 = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        assert cmd1 != cmd2

    def test_str_when_called_then_returns_representation(self) -> None:
        cmd = OpenPullRequestCommand(
            version="1.0.0",
            branch="release/v1.0.0",
            dry_run=False,
        )

        result = str(cmd)

        assert "OpenPullRequestCommand" in result
