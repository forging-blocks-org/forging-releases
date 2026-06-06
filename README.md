# forging-releases

> **Work in Progress** — The interface and presentation are not yet final. Things will change.

---

## What This Does

`forging-releases` automates the repetitive, error-prone parts of shipping a new software release. Instead of manually bumping version numbers, writing changelogs, creating branches, opening pull requests, and pushing tags, you describe *what kind of release you want* and the tool handles the rest.

---

## The Interface

The tool is designed as a CLI with a two-phase flow: **preview first, execute second.**

```
release <release_level>
release <release_level> --execute
```

The first form shows you what *would* happen — the version bump, the branch name, the tag, the changelog entries. Nothing is written to disk, no branches are pushed, no PRs are opened.

The second form (`--execute`) actually performs the release. It:

1. Reads the current version from `pyproject.toml`
2. Computes the next version based on the level you chose
3. Creates a release branch (e.g., `release/v1.2.4`)
4. Applies the version bump to `pyproject.toml`
5. Generates a changelog from commits since the last tag
6. Commits the changes and pushes the branch with tags
7. Opens a pull request against the main branch

`release_level` is one of `major`, `minor`, or `patch`. (Release candidates are planned but not yet presented.)

### Examples

```
# Preview a patch release
release patch

# Preview a minor release
release minor

# Execute a patch release
release patch --execute
```

---

## Why This Exists

Releases are a checklist of mechanical steps. Each step is simple, but the sequence is easy to mess up: forgetting to tag, pushing to the wrong branch, merging a PR without bumping the version first, or writing a changelog from memory.

This project encodes that checklist into code — with validation, rollback on failure, and a preview mode so you never run blind.

---

## Architecture

The project follows **Hexagonal Architecture (Ports & Adapters)** with **Domain-Driven Design**:

```
CLI / CI system
      |
      v
  [Use Case]         ← abstract inbound port (what the caller sees)
      |
      v
  [Service]          ← orchestrates business rules
      |
      v
  [Domain]           ← value objects, entities, pure logic
      |
      v
  [Ports]            ← interfaces for I/O (versioning, git, GitHub, changelog)
      |
      v
  [Infrastructure]   ← concrete implementations (pyproject.toml, git CLI, GitHub API)
```

Everything I/O-related is behind an interface, so the domain logic stays testable without touching the filesystem or network. The release itself runs inside a **transaction with compensation** — if any step fails, earlier steps are rolled back automatically.

---

## Status

- [x] Core domain model (version, branch, tag, PR)
- [x] Git operations (branch, commit, push, tag)
- [x] Version bumping in `pyproject.toml`
- [x] Changelog generation from git history
- [x] GitHub pull request creation
- [x] Preview / dry-run mode
- [x] Transactional rollback on failure
- [ ] CLI wiring (the `release` command is designed but not yet connected)
- [ ] Release candidate support
- [ ] MkDocs documentation site
- [ ] Final interface design and presentation

---

## Development

Python 3.14+. Managed with `uv`.

```sh
uv sync --all-extras --dev
pytest --cov
ruff check
ruff format --check
```
