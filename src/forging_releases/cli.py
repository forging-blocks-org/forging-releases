"""Click CLI for forging-releases — a standalone release automation tool."""

from __future__ import annotations

import asyncio
import subprocess
import sys

import click

from forging_releases.application.ports.inbound.prepare_release_use_case import (
    PrepareReleaseInput,
)
from forging_releases.infrastructure.container import Container

_ENSURE_ON_MAIN = (
    'git rev-parse --abbrev-ref HEAD | grep -qx main || '
    '(echo "ERROR: must start from main" && exit 1)'
)
_ENSURE_CLEAN_TREE = (
    'git diff --quiet || '
    '(echo "ERROR: working tree not clean" && exit 1)'
)
_FETCH_TAGS = "git fetch origin --tags"
_ENSURE_MAIN_SYNCED = (
    'git diff --quiet origin/main...HEAD || '
    '(echo "ERROR: local main differs from origin/main" && exit 1)'
)
_BUILD_CHECK = "uv build"

_VALIDATE_CHECKS: list[str] = [
    _ENSURE_ON_MAIN,
    _ENSURE_CLEAN_TREE,
    _FETCH_TAGS,
    _ENSURE_MAIN_SYNCED,
    _BUILD_CHECK,
]




@click.group()
def main() -> None:
    """forging-releases — automated release pipeline for Python projects."""




@main.command()
@click.argument(
    "level",
    default="patch",
    type=click.Choice(["major", "minor", "patch"]),
)
@click.option(
    "--execute",
    is_flag=True,
    default=False,
    help="Execute with side effects (default: dry-run)",
)
def release(level: str, execute: bool) -> None:
    """Prepare and optionally execute a release.

    LEVEL is the semantic version bump: major, minor, or patch (default: patch).

    By default runs in dry-run mode — use --execute to apply real changes.
    """

    async def _run() -> None:
        container = Container()
        await container.initialize()
        use_case = container.get_prepare_release_use_case()
        output = await use_case.execute(
            PrepareReleaseInput(level=level, dry_run=not execute)
        )
        click.echo(f"Version:    {output.version}")
        if not execute:
            click.echo("[DRY-RUN] No changes applied. Use --execute to apply.")

    asyncio.run(_run())




@main.command(name="validate")
def validate_cmd() -> None:
    """Validate release readiness: branch, cleanliness, and build checks."""
    _run_shell_checks(_VALIDATE_CHECKS)




@main.command(name="validate-remote")
def validate_remote_cmd() -> None:
    """Validate remote CI/CD: check the validate-release workflow status."""
    click.echo("Validating remote release workflow...")
    result = subprocess.run(
        ["bash", "scripts/validate_release_remote.sh"],
        check=False,
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.stderr:
        click.echo(result.stderr, err=True)
    if result.returncode != 0:
        sys.exit(result.returncode)




@main.command(name="validate-github")
def validate_github_cmd() -> None:
    """Trigger the validate-release GitHub Actions workflow."""
    try:
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        )
        branch = branch_result.stdout.strip()

        click.echo("Validating GitHub workflow without publishing...")
        click.echo(f"Branch: {branch}")

        subprocess.run(
            [
                "gh", "workflow", "run", "validate-release.yml",
                "-f", f"release_branch={branch}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        click.echo("\nValidation workflow triggered. Check status with:")
        click.echo("  gh run list --workflow validate-release.yml")
    except subprocess.CalledProcessError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)




def _run_shell_checks(checks: list[str]) -> None:
    """Run a sequence of shell commands, failing on first error."""
    for cmd in checks:
        click.echo(f"  $ {cmd}")
        result = subprocess.run(
            ["bash", "-c", cmd],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip()
            click.echo(f"FAILED: {msg}", err=True)
            sys.exit(1)
        if result.stdout.strip():
            click.echo(result.stdout.strip())
    click.echo("OK: release validated")


if __name__ == "__main__":
    main()
