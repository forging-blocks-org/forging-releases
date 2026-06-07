from __future__ import annotations

import subprocess

from forging_releases.application.ports.outbound.changelog_generator import (
    ChangelogGenerator,
    ChangelogRequest,
    ChangelogResponse,
)


class GitChangelogGenerator(ChangelogGenerator):
    _DRY_RUN_PREFIX: str = "[dry-run]"

    def __init__(self, *, cwd: str | None = None) -> None:
        self._cwd = cwd

    async def generate(self, request: ChangelogRequest) -> ChangelogResponse:
        if request.dry_run:
            return ChangelogResponse(entries=["[dry-run] changelog entry"])

        tag = f"v{request.from_version}"
        result = subprocess.run(
            ["git", "log", f"{tag}..HEAD", "--pretty=format:- %s"],
            cwd=self._cwd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return ChangelogResponse(entries=[])

        entries = [line.strip() for line in result.stdout.strip().splitlines()]
        return ChangelogResponse(entries=entries)
