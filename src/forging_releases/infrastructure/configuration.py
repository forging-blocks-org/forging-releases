from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ReleaseConfiguration:
    """Project-specific settings assembled by the composition root."""

    project_file: Path = Path("pyproject.toml")
    changelog_file: Path = Path("CHANGELOG.md")
    cliff_config_file: Path = Path("cliff.toml")
    base_branch: str = "main"
    remote: str = "origin"
    release_branch_prefix: str = "release/v"
