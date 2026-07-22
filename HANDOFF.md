# Forging Releases — Extraction Handoff

**Date:** 2026-07-22
**Status:** Complete (uncommitted), all tests green, pyright clean

## What happened

Extracted release automation from the forging-blocks monorepo into this standalone `uv` project.

## Directory layout

```
forging-releases/
├── pyproject.toml          # standalone uv project
├── cliff.toml              # git-cliff changelog config
├── README.md
├── HANDOFF.md              # this file
├── src/forging_releases/   # package source
│   ├── cli.py              # click CLI (release, validate, validate-remote, validate-github)
│   └── ...
└── tests/                  # 142 pass, 13 skip
```

## Dependencies

- **Production:** `click>=8.4.2`, `forging-blocks>=0.4.0`, `tomlkit>=0.15.1`
- **Dev:** `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `pyright`

Entry point: `forging-releases = "forging_releases.cli:main"`

## CLI commands

| Command | What it does |
|---|---|
| `forging-releases release` | Interactive release workflow |
| `forging-releases validate` | Validate CWD project for release |
| `forging-releases validate-remote` | Validate remote state for release |
| `forging-releases validate-github` | Trigger GitHub validate-release workflow |

## Temporary source override

`pyproject.toml` has a local path source for development:

```toml
[tool.uv.sources]
forging-blocks = { path = "../forging-blocks", editable = true }
```

This resolves against the sibling forging-blocks repo so all APIs (including 
`MessageHandlerPort`, etc.) are available. Remove this before publishing to 
PyPI since the release will pin `forging-blocks>=0.4.0` at that point.

## Verification

```bash
uv sync
uv run pytest -c pyproject.toml -x -q
# 142 passed, 13 skipped

uv run pyright
# 0 errors, 0 warnings
```

## What was cleaned up in the forging-blocks repo

- `forging-releases/` directory removed from main repo
- `[tool.uv.workspace]` removed from main repo pyproject.toml
- Duplicate `[tool.uv.workspace]` removed from worktree pyproject.toml

## Remaining in the forging-blocks repo

- `scripts/release/` — original release code (preserved; this is what was extracted)
- `scripts/validate_release_remote.sh` — original shell script
- poe `release:*` tasks in pyproject.toml

## Known issues

1. **Temporary path source**: See above — revert before publishing
2. **validate-github**: `validate-release.yml` workflow doesn't exist yet (P2)
3. **Worktree residue**: `.worktrees/chore-forging-releases-inital-initiative` still exists in forging-blocks
