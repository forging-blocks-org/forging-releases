import pytest
from forging_releases.application.errors import CommandExecutionError
from forging_releases.infrastructure.commons.process import SubprocessCommandRunner


@pytest.mark.unit
class TestSubprocessCommandRunner:
    def test_run_success_preserves_stdout(self) -> None:
        result = SubprocessCommandRunner().run(["printf", "hello\\n"])

        assert result == "hello\\n"

    def test_run_failure_exposes_structured_process_result(self) -> None:
        with pytest.raises(CommandExecutionError) as exc_info:
            SubprocessCommandRunner().run(
                ["sh", "-c", "printf output; printf error >&2; exit 7"]
            )

        error = exc_info.value
        assert error.command == ("sh", "-c", "printf output; printf error >&2; exit 7")
        assert error.returncode == 7
        assert error.stdout == "output"
        assert error.stderr == "error"

    def test_run_with_check_false_returns_output_on_failure(self) -> None:
        result = SubprocessCommandRunner().run(
            ["sh", "-c", "printf output; exit 7"], check=False
        )

        assert result == "output"
