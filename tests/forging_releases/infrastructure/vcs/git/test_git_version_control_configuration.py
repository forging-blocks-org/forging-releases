from __future__ import annotations

import pytest
from forging_releases.application.errors import CommandExecutionError, VersionControlError
from forging_releases.domain.value_objects import ReleaseBranchName
from forging_releases.infrastructure.vcs.git.git_version_control import GitVersionControl

from tests.fixtures.fake_command_runner import FakeCommandRunner


@pytest.mark.unit
class TestGitVersionControlConfiguration:
    def test_checkout_main_fallback_uses_configured_base_and_remote(self) -> None:
        runner = FakeCommandRunner(
            CommandExecutionError(
                ("git", "checkout", "trunk"),
                1,
                "",
                "error: pathspec 'trunk' did not match any file(s) known to git",
            ),
            "upstream/trunk",
            "",
        )
        version_control = GitVersionControl(
            runner,
            base_branch="trunk",
            remote="upstream",
            release_branch_prefix="hotfix/",
        )

        version_control.checkout_main()

        assert [call[0] for call in runner.calls] == [
            ["git", "checkout", "trunk"],
            ["git", "symbolic-ref", "--short", "refs/remotes/upstream/HEAD"],
            ["git", "checkout", "trunk"],
        ]

    def test_checkout_main_fallback_preserves_nested_default_branch(self) -> None:
        runner = FakeCommandRunner(
            CommandExecutionError(
                ("git", "checkout", "main"),
                1,
                "",
                "error: pathspec 'main' did not match any file(s) known to git",
            ),
            "origin/team/main",
            "",
        )

        GitVersionControl(runner).checkout_main()

        assert runner.calls[-1][0] == ["git", "checkout", "team/main"]

    def test_remote_branch_operations_use_configured_remote(self) -> None:
        branch = ReleaseBranchName("release/v1.2.3")
        runner = FakeCommandRunner("remote branch")
        version_control = GitVersionControl(runner, remote="upstream")

        assert version_control.remote_branch_exists(branch) is True
        version_control.push(branch)
        version_control.delete_remote_branch(branch)

        assert [call[0] for call in runner.calls] == [
            ["git", "ls-remote", "--exit-code", "--heads", "upstream", "release/v1.2.3"],
            ["git", "push", "upstream", "release/v1.2.3"],
            ["git", "push", "upstream", "--delete", "release/v1.2.3"],
        ]
        assert runner.calls[2][1] is False

    def test_commit_failure_exposes_actual_return_code_in_adapter_error(self) -> None:
        runner = FakeCommandRunner(
            "",
            CommandExecutionError(
                ("git", "commit"),
                23,
                "",
                "index is locked",
            ),
        )
        version_control = GitVersionControl(runner)

        with pytest.raises(VersionControlError) as exc_info:
            version_control.commit_release_artifacts()

        assert exc_info.value.operation == "commit"
        assert "23" in exc_info.value.message.value
        assert "index is locked" in exc_info.value.message.value
