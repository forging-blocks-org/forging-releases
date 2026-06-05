from __future__ import annotations

import os
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
            print(f"{self._DRY_RUN_PREFIX} Would generate changelog from {request.from_version}")
            return ChangelogResponse(entries=["[dry-run] changelog entry"])

        entries = self._extract_commits(request.from_version)
        return ChangelogResponse(entries=entries)

    def _extract_commits(self, from_version: str) -> list[str]:
        tag = f"v{from_version}"
        result = self._run_git(
            ["log", f"{tag}..HEAD", "--pretty=format:- %s"],
            check=False,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]

    def _run_git(
        self,
        args: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self._cwd,
            capture_output=True,
            text=True,
            check=check,
            env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1"},
        )
