from __future__ import annotations

from pathlib import Path

import pytest
from forging_releases.application.errors import ChangelogGenerationError, CommandExecutionError
from forging_releases.application.ports.outbound import ChangelogRequest
from forging_releases.infrastructure.changelog.git_cliff_changelog_generator import (
    GitCliffChangelogGenerator,
)

from tests.fixtures.fake_command_runner import FakeCommandRunner


@pytest.mark.unit
class TestGitCliffChangelogGeneratorEdgeCases:
    async def test_generate_passes_configured_cliff_file_to_git_cliff(self, tmp_path: Path) -> None:
        config_path = tmp_path / "release-cliff.toml"
        config_path.write_text("[changelog]\noutput = \"-\"\n", encoding="utf-8")
        runner = FakeCommandRunner("abc123", "## [1.0.0]\n- feature\n")
        generator = GitCliffChangelogGenerator(
            runner=runner,
            changelog_path=tmp_path / "release-notes.md",
            cliff_config_path=config_path,
        )

        await generator.generate(ChangelogRequest(from_version="1.0.0"))

        assert runner.calls[1][0][:4] == [
            "git-cliff",
            "--config",
            str(config_path),
            "--output",
        ]

    async def test_generate_wraps_nonzero_git_cliff_exit_with_stderr(self, tmp_path: Path) -> None:
        changelog_path = tmp_path / "CHANGELOG.md"
        original = "## [0.9.0]\n\n- previous\n"
        changelog_path.write_text(original, encoding="utf-8")
        runner = FakeCommandRunner(
            "abc123",
            CommandExecutionError(
                ("git-cliff", "--output", "-"),
                17,
                "",
                "invalid configuration",
            ),
        )
        generator = GitCliffChangelogGenerator(runner=runner, changelog_path=changelog_path)

        with pytest.raises(ChangelogGenerationError, match="invalid configuration"):
            await generator.generate(ChangelogRequest(from_version="1.0.0"))

        assert changelog_path.read_text(encoding="utf-8") == original

    async def test_generate_wraps_missing_git_executable_as_changelog_error(self, tmp_path: Path) -> None:
        runner = FakeCommandRunner(FileNotFoundError("git"))
        generator = GitCliffChangelogGenerator(
            runner=runner,
            changelog_path=tmp_path / "CHANGELOG.md",
        )

        with pytest.raises(ChangelogGenerationError, match="git is not installed"):
            await generator.generate(ChangelogRequest(from_version="1.0.0"))

    async def test_generate_does_not_rewrite_existing_file_for_empty_output(self, tmp_path: Path) -> None:
        changelog_path = tmp_path / "CHANGELOG.md"
        original = "# Changelog\n\n## [0.9.0]\n\n- previous\n"
        changelog_path.write_text(original, encoding="utf-8")
        runner = FakeCommandRunner("abc123", "\n\n")
        generator = GitCliffChangelogGenerator(runner=runner, changelog_path=changelog_path)

        response = await generator.generate(ChangelogRequest(from_version="1.0.0"))

        assert response.entries == []
        assert changelog_path.read_text(encoding="utf-8") == original

    async def test_generate_reports_missing_cliff_config(self, tmp_path: Path) -> None:
        runner = FakeCommandRunner("abc123", "## [1.0.0]\n- feature\n")
        generator = GitCliffChangelogGenerator(
            runner=runner,
            changelog_path=tmp_path / "CHANGELOG.md",
            cliff_config_path=tmp_path / "missing-cliff.toml",
        )

        with pytest.raises(ChangelogGenerationError, match="configuration file"):
            await generator.generate(ChangelogRequest(from_version="1.0.0"))

        assert runner.calls == []
