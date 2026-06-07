# Hooks & Commits

## Pre-commit Hooks

```sh
# Install hooks (run once)
uv run pre-commit install

# Run on all files (after install)
uv run pre-commit run --all-files

# Run a specific hook on all files
uv run pre-commit run ruff --all-files
uv run pre-commit run pytest --all-files

# Skip hooks on a single commit (emergency use only)
git commit -m "..." --no-verify

# Update hook versions
uv run pre-commit autoupdate
```

The project runs ruff lint, ruff format, file checks (trailing whitespace, yaml, toml, merge conflicts), and pytest on every commit.

> **Note**: `uv run pre-commit` resolves `pre-commit` via the project environment.
> If you installed `pre-commit` globally and it also works, use whichever method is consistent for the team.

---

## Commit Plan

The working tree contains 65 files changed across 3 concerns. Stage each commit independently.

### Commit 1 — Test naming conventions

Consolidate fragmented test files, rename test classes to match source names, rename methods to follow `test_<method>_when_<scenario>_then_<result>`.

```sh
git add tests/forging_releases/infrastructure/versioning_service/test_pyproject_versioning_service.py tests/forging_releases/infrastructure/version_control/test_git_version_control.py tests/forging_releases/application/services/test_prepare_release_service.py tests/forging_releases/application/services/test_open_release_pull_request_service.py tests/forging_releases/infrastructure/command_runner/test_subprocess_command_runner.py tests/forging_releases/infrastructure/handler/test_open_pull_request_handler.py tests/forging_releases/infrastructure/pull_request_service/test_github_pull_request_service.py tests/forging_releases/infrastructure/changelog_generator/test_git_changelog_generator.py tests/forging_releases/infrastructure/release_transaction/test_in_memory_release_transaction.py tests/forging_releases/infrastructure/command_bus/test_in_memory_release_command_bus.py

git commit -m "refactor(tests): consolidate test files and adopt naming conventions

- Merge 5 versioning_service test files into test_pyproject_versioning_service.py
- Merge 9 version_control test files into test_git_version_control.py
- Rename test classes to Test{SourceClassName}
- Rename methods to test_<method>_when_<scenario>_then_<result>
- Use @pytest.mark.parametrize for repetitive bump/error scenarios"
```

### Commit 2 — Shared fixtures & AAA readability

Extract duplicate HTTP server fixtures to `tests/fixtures/` and add AAA spacing to all test bodies.

```sh
git add tests/fixtures/handler_scenarios.py tests/forging_releases/infrastructure/handler/test_open_pull_request_handler.py tests/forging_releases/infrastructure/pull_request_service/test_github_pull_request_service.py tests/forging_releases/application/services/test_prepare_release_service.py tests/forging_releases/application/services/test_open_release_pull_request_service.py tests/forging_releases/infrastructure/command_runner/test_subprocess_command_runner.py tests/forging_releases/infrastructure/changelog_generator/test_git_changelog_generator.py tests/forging_releases/infrastructure/release_transaction/test_in_memory_release_transaction.py tests/forging_releases/infrastructure/command_bus/test_in_memory_release_command_bus.py tests/forging_releases/infrastructure/test_container.py tests/forging_releases/infrastructure/versioning_service/test_pyproject_versioning_service.py tests/forging_releases/infrastructure/version_control/test_git_version_control.py

git commit -m "refactor(tests): extract shared fixtures and add AAA spacing

- Consolidate duplicate HTTP PR server fixtures into tests/fixtures/handler_scenarios.py
- Remove local _RequestCaptureHandler / _PRHandler duplicates from handler and PR tests
- Separate Arrange/Act/Assert sections with blank lines across all test files
- Use ReleaseVersion objects directly in parametrized test arguments"
```

### Commit 3 — Source docstrings

Add Google-style docstrings to all modules, classes, and public methods across the source tree.

```sh
git add src/forging_releases/application/ src/forging_releases/domain/ src/forging_releases/infrastructure/

git commit -m "docs: add Google-style docstrings to all source modules, classes, and methods

- Module docstrings describing each file's purpose
- Class docstrings with attribute documentation (dataclasses)
- Method docstrings with Args/Returns sections
- Covers application services, ports, errors, workflow,
  domain value objects, entities, commands, errors,
  and all infrastructure implementations"
```

---

## Verify After Each Commit

```sh
uv run pytest
uv run ruff check
uv run pyright
```

---

## Quick Checklist

| Step | Command |
|---|---|
| Install hooks | `uv run pre-commit install` |
| Run all hooks | `uv run pre-commit run --all-files` |
| Test only | `uv run pytest` |
| Lint only | `uv run ruff check` |
| Types only | `uv run pyright` |
| Full check | `uv run pytest && uv run ruff check && uv run pyright` |
