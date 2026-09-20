from argparse import Namespace
from pathlib import Path

import pytest

from forging_releases.presentation.parsers.release_cli_parser import ReleaseCliParser


@pytest.mark.unit
class TestReleaseCliParser:
    def test_parse_defaults_to_patch_and_dry_run(self) -> None:
        assert ReleaseCliParser().parse([]) == Namespace(
            level="patch",
            execute=False,
            project_file=Path("pyproject.toml"),
            changelog_file=Path("CHANGELOG.md"),
            cliff_config_file=Path("cliff.toml"),
            base_branch="main",
            remote="origin",
            release_branch_prefix="release/v",
        )

    @pytest.mark.parametrize("argv", [["major", "--execute"], ["--execute", "minor"]])
    def test_parse_accepts_level_and_execute_in_any_order(self, argv: list[str]) -> None:
        parsed = ReleaseCliParser().parse(argv)
        assert parsed.level in {"major", "minor"}
        assert parsed.execute is True

    def test_parse_accepts_every_configuration_option(self) -> None:
        parsed = ReleaseCliParser().parse(
            [
                "--project-file", "project.toml", "--changelog-file", "release-notes.md",
                "--cliff-config-file", "release-cliff.toml", "--base-branch", "trunk",
                "--remote", "upstream", "--release-branch-prefix", "stable/",
            ]
        )
        assert parsed.project_file == Path("project.toml")
        assert parsed.changelog_file == Path("release-notes.md")
        assert parsed.cliff_config_file == Path("release-cliff.toml")
        assert parsed.base_branch == "trunk"
        assert parsed.remote == "upstream"
        assert parsed.release_branch_prefix == "stable/"

    @pytest.mark.parametrize("argv", [["invalid"], ["--unknown"]])
    def test_parse_rejects_invalid_arguments(self, argv: list[str]) -> None:
        with pytest.raises(SystemExit) as raised:
            ReleaseCliParser().parse(argv)
        assert raised.value.code == 2

    def test_parse_none_uses_process_arguments(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.argv", ["release", "minor", "--execute"])
        parsed = ReleaseCliParser().parse(None)
        assert parsed.level == "minor"
        assert parsed.execute is True

    def test_help_exits_successfully(self) -> None:
        with pytest.raises(SystemExit) as raised:
            ReleaseCliParser().parse(["--help"])
        assert raised.value.code == 0
