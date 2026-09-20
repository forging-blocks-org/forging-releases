# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
from __future__ import annotations

import pytest
from forging_releases.application.errors import CommandExecutionError, VersionControlError
from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.vcs.git.git_version_control import GitVersionControl

from tests.fixtures.fake_command_runner import FakeCommandRunner


@pytest.mark.unit
class TestGitVersionControl:
    @pytest.fixture
    def runner(self) -> FakeCommandRunner:
        return FakeCommandRunner()

    @pytest.fixture
    def version_control(self, runner: FakeCommandRunner) -> GitVersionControl:
        return GitVersionControl(runner)

    @pytest.fixture
    def branch_name(self) -> ReleaseBranchName:
        return ReleaseBranchName("release/v1.2.0")

    def test_branch_exists_when_branch_found_then_returns_true(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        result = version_control.branch_exists(branch_name)

        assert result is True
        assert len(runner.calls) == 1
        assert runner.calls[0] == (
            ["git", "rev-parse", "--verify", "release/v1.2.0"],
            True,
        )

    def test_branch_exists_when_branch_not_found_then_returns_false(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        runner.configured_outputs = [
            CommandExecutionError(
                ("git", "rev-parse", "--verify", "release/v1.2.0"),
                1,
                "",
                "fatal: branch not found",
            )
        ]

        result = version_control.branch_exists(branch_name)

        assert result is False

    def test_checkout(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        version_control.checkout(branch_name)

        assert len(runner.calls) == 1
        assert runner.calls[0][0] == ["git", "checkout", "release/v1.2.0"]

    def test_checkout_main_success(
        self, version_control: GitVersionControl, runner: FakeCommandRunner
    ) -> None:
        version_control.checkout_main()

    def test_checkout_main_fallback(
        self, version_control: GitVersionControl, runner: FakeCommandRunner
    ) -> None:
        runner.configured_outputs = [
            CommandExecutionError(
                ("git", "checkout", "main"),
                1,
                "",
                "error: pathspec 'main' did not match any file(s) known to git",
            ),
            "origin/master",  # symbolic-ref
            "",  # checkout master
        ]

        version_control.checkout_main()

        assert len(runner.calls) == 3
        assert runner.calls[0][0] == ["git", "checkout", "main"]
        assert runner.calls[1][0] == ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]
        assert runner.calls[2][0] == ["git", "checkout", "master"]

    def test_checkout_main_does_not_fallback_when_git_is_missing(
        self,
        runner: FakeCommandRunner,
    ) -> None:
        runner.configured_outputs = [FileNotFoundError("git")]

        with pytest.raises(VersionControlError) as exc_info:
            GitVersionControl(runner).checkout_main()

        assert exc_info.value.operation == "checkout"
        assert len(runner.calls) == 1

    def test_commit_release_artifacts(
        self, version_control: GitVersionControl, runner: FakeCommandRunner
    ) -> None:
        version_control.commit_release_artifacts()

        assert len(runner.calls) == 2
        assert runner.calls[0][0] == ["git", "add", "-A"]
        assert runner.calls[1][0] == ["git", "commit", "-m", "chore(release): prepare release"]

    def test_commit_release_artifacts_retry_precommit(
        self, version_control: GitVersionControl, runner: FakeCommandRunner
    ) -> None:
        runner.configured_outputs = [
            "",  # git add -A
            CommandExecutionError(
                ("git", "commit", "-m", "chore(release): prepare release"),
                1,
                "",
                "pre-commit failure",
            ),  # first commit attempt
            "",  # git add -A (retry)
            "",  # second commit attempt
        ]

        version_control.commit_release_artifacts()


    def test_commit_release_artifacts_failure(
        self, version_control: GitVersionControl, runner: FakeCommandRunner
    ) -> None:
        runner.configured_outputs = [
            "",
            CommandExecutionError(
                ("git", "commit", "-m", "chore(release): prepare release"),
                1,
                "",
                "error",
            ),
        ]

        with pytest.raises(RuntimeError):
            version_control.commit_release_artifacts()

    def test_create_branch(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        version_control.create_branch(branch_name)

        assert len(runner.calls) == 1
        assert runner.calls[0][0] == ["git", "checkout", "-b", "release/v1.2.0"]

    def test_delete_local_branch(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        version_control.delete_local_branch(branch_name)

        assert len(runner.calls) == 1
        assert runner.calls[0][0] == ["git", "branch", "-D", "release/v1.2.0"]
        assert runner.calls[0][1] is False

    def test_delete_remote_branch(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        version_control.delete_remote_branch(branch_name)

        assert len(runner.calls) == 1
        assert runner.calls[0][0] == ["git", "push", "origin", "--delete", "release/v1.2.0"]
        assert runner.calls[0][1] is False

    def test_push(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        version_control.push(branch_name)

        assert len(runner.calls) == 1
        assert runner.calls[0][0] == ["git", "push", "origin", "release/v1.2.0"]

    def test_remote_branch_exists_true(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        result = version_control.remote_branch_exists(branch_name)

        assert result is True

    def test_remote_branch_exists_false(
        self,
        version_control: GitVersionControl,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        runner.configured_outputs = [
            CommandExecutionError(
                ("git", "ls-remote", "--exit-code", "--heads", "origin", branch_name.value),
                2,
                "",
                "remote branch not found",
            )
        ]

        result = version_control.remote_branch_exists(branch_name)

        assert result is False
    
    def test_checkout_wraps_command_failure_with_operation_message(
        self,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        runner.configured_outputs = [
            CommandExecutionError(
                ("git", "checkout", branch_name.value),
                4,
                "",
                "permission denied",
            )
        ]

        with pytest.raises(VersionControlError) as exc_info:
            GitVersionControl(runner).checkout(branch_name)

        assert exc_info.value.operation == "checkout"
        assert "permission denied" in exc_info.value.message.value

    def test_checkout_wraps_missing_git_executable(
        self,
        runner: FakeCommandRunner,
        branch_name: ReleaseBranchName,
    ) -> None:
        runner.configured_outputs = [FileNotFoundError("git")]

        with pytest.raises(VersionControlError) as exc_info:
            GitVersionControl(runner).checkout(branch_name)

        assert exc_info.value.operation == "checkout"
        assert "not found in PATH" in exc_info.value.message.value

    def test_remote_lookup_failure_preserves_actual_return_code(
        self,
        runner: FakeCommandRunner,
    ) -> None:
        runner.configured_outputs = [
            CommandExecutionError(
                ("git", "checkout", "main"),
                1,
                "",
                "error: pathspec 'main' did not match any file(s) known to git",
            ),
            CommandExecutionError(
                (
                    "git",
                    "symbolic-ref",
                    "--short",
                    "refs/remotes/origin/HEAD",
                ),
                9,
                "",
                "",
            ),
        ]

        with pytest.raises(VersionControlError) as exc_info:
            GitVersionControl(runner).checkout_main()

        assert exc_info.value.operation == "remote lookup"
        assert "9" in exc_info.value.message.value
