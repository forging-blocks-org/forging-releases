"""Argument parsing for the forging-releases command-line interface."""

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path


class ReleaseCliParser:
    """Parse release level, execution mode, and project configuration options."""

    def __init__(self) -> None:
        self._argument_parser = self._create_argument_parser()

    def parse(self, argv: Sequence[str] | None = None) -> Namespace:
        """Parse ``argv`` or the process command line when it is omitted."""
        return self._argument_parser.parse_args(argv)

    @staticmethod
    def _create_argument_parser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="release",
            description="Release automation CLI (presentation layer).",
        )
        parser.add_argument(
            "level",
            choices=("major", "minor", "patch"),
            nargs="?",
            default="patch",
            help="Release level: major, minor, or patch.",
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            default=False,
            help="Execute the release with side effects (default is a simulation).",
        )
        parser.add_argument(
            "--project-file",
            type=Path,
            default=Path("pyproject.toml"),
            help="PEP 621 project metadata file (default: pyproject.toml).",
        )
        parser.add_argument(
            "--changelog-file",
            type=Path,
            default=Path("CHANGELOG.md"),
            help="Changelog file (default: CHANGELOG.md).",
        )
        parser.add_argument(
            "--cliff-config-file",
            type=Path,
            default=Path("cliff.toml"),
            help="git-cliff configuration file (default: cliff.toml).",
        )
        parser.add_argument(
            "--base-branch",
            default="main",
            help="Base branch for the release (default: main).",
        )
        parser.add_argument(
            "--remote",
            default="origin",
            help="Git remote used for release operations (default: origin).",
        )
        parser.add_argument(
            "--release-branch-prefix",
            default="release/v",
            help="Prefix used for release branches (default: release/v).",
        )
        return parser
