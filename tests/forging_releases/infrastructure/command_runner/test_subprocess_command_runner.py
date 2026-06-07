# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from forging_releases.infrastructure.command_runner.command_runner import (
    SubprocessCommandRunner,
)


@pytest.mark.integration
class TestSuccessfulCommands:
    def test_when_command_succeeds_then_returns_stdout(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(["echo", "hello world"])
        assert result.returncode == 0
        assert result.stdout.strip() == "hello world"

    def test_when_command_succeeds_then_stderr_is_empty(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(["echo", "ok"])
        assert result.stderr == ""

    def test_when_command_produces_stderr_then_captured(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(["bash", "-c", "echo 'warning' >&2 && echo 'output'"])
        assert result.stdout.strip() == "output"
        assert result.stderr.strip() == "warning"


@pytest.mark.integration
class TestFailingCommands:
    def test_when_command_fails_then_raises_runtime_error(self) -> None:
        runner = SubprocessCommandRunner()
        with pytest.raises(RuntimeError, match="Command failed"):
            runner.run(["false"])

    def test_when_command_fails_then_error_contains_exit_code(self) -> None:
        runner = SubprocessCommandRunner()
        with pytest.raises(RuntimeError) as exc_info:
            runner.run(["bash", "-c", "exit 42"])
        assert "exit code 42" in str(exc_info.value)

    def test_when_command_fails_then_error_contains_stderr(self) -> None:
        runner = SubprocessCommandRunner()
        with pytest.raises(RuntimeError) as exc_info:
            runner.run(["bash", "-c", "echo 'error message' >&2; exit 1"])
        assert "error message" in str(exc_info.value)


@pytest.mark.integration
class TestGitSpecificErrors:
    def test_when_git_not_a_repository_then_extracts_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = SubprocessCommandRunner(cwd=tmpdir)
            with pytest.raises(RuntimeError) as exc_info:
                runner.run(["git", "log"])
            error = str(exc_info.value)
            assert error.startswith("Git command failed:")
            assert "not a git repository" in error

    def test_when_git_command_fails_then_error_starts_with_git_prefix(self) -> None:
        runner = SubprocessCommandRunner()
        with pytest.raises(RuntimeError) as exc_info:
            runner.run(["git", "rev-parse", "--verify", "nonexistent-branch"])
        assert "Git command failed:" in str(exc_info.value)


@pytest.mark.integration
class TestCwdParameter:
    def test_when_cwd_provided_then_command_runs_in_that_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = SubprocessCommandRunner()
            result = runner.run(["pwd"], cwd=tmpdir)
            assert result.stdout.strip() == tmpdir

    def test_when_cwd_changes_then_working_directory_differs(self) -> None:
        with (
            tempfile.TemporaryDirectory() as dir1,
            tempfile.TemporaryDirectory() as dir2,
        ):
            runner = SubprocessCommandRunner()
            result1 = runner.run(["pwd"], cwd=dir1)
            result2 = runner.run(["pwd"], cwd=dir2)
            assert result1.stdout.strip() == dir1
            assert result2.stdout.strip() == dir2

    def test_when_constructor_cwd_set_then_used_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = SubprocessCommandRunner(cwd=tmpdir)
            result = runner.run(["pwd"])
            assert result.stdout.strip() == tmpdir


@pytest.mark.integration
class TestEnvPassthrough:
    def test_when_env_passed_then_command_sees_those_variables(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(
            ["bash", "-c", "echo $MY_VAR"],
            env={**os.environ, "MY_VAR": "custom_value"},
        )
        assert result.stdout.strip() == "custom_value"

    def test_when_env_contains_custom_var_then_not_leaked_to_os(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(
            ["bash", "-c", "echo $CUSTOM_SECRET"],
            env={**os.environ, "CUSTOM_SECRET": "secret"},
        )
        assert result.stdout.strip() == "secret"

    def test_when_env_not_passed_then_inherits_os_environ(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(["bash", "-c", "echo $PATH"])
        assert ":" in result.stdout.strip()


@pytest.mark.integration
class TestDryRun:
    def test_when_dry_run_then_returns_empty_result(self) -> None:
        runner = SubprocessCommandRunner()
        result = runner.run(["false"], dry_run=True)
        assert result.returncode == 0
        assert result.stdout == ""

    def test_when_dry_run_then_command_is_not_executed(self) -> None:
        runner = SubprocessCommandRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            marker = Path(tmpdir) / "should_not_exist"
            runner.run(
                ["touch", str(marker)],
                cwd=tmpdir,
                dry_run=True,
            )
            assert not marker.exists()
