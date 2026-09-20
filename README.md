# forging-releases

Reusable release preparation for Python projects that declare PEP 621 metadata.
The package prepares a versioned release branch, updates the changelog, and opens a
GitHub pull request through the configured adapters.

## Requirements

- Python 3.14 or newer.
- A `pyproject.toml` with a PEP 621 `[project]` table and a string
  `[project].version` field. Poetry-only metadata is not supported.
- `git` for repository operations.
- `git-cliff` for changelog generation.
- GitHub CLI (`gh`) for pull-request creation.
- An authenticated GitHub CLI session for an executing release:

  ```bash
  gh auth login
  gh auth status
  ```

The default files are `pyproject.toml`, `CHANGELOG.md`, and `cliff.toml`. The
release defaults to the `main` branch, uses the `origin` remote, and names release
branches with the `release/v` prefix.

## Installation

Install the published package from an index with either `uv` or `pip`:

```bash
uv add forging-releases
python -m pip install forging-releases
```

The package depends on `forging-blocks==0.5.0` and `tomlkit>=0.15.1`. It does not
require a checkout of either project at runtime.

## Command-line interface

The installed command is `forging-releases`. The release level is an optional
positional argument, so the default level is `patch`:

```bash
forging-releases --help
forging-releases
forging-releases minor
forging-releases --execute patch
```

Execution is a dry run by default. A dry run calculates the release and exercises
read-only checks without applying version, changelog, branch, tag, commit, push, or
pull-request changes. Pass `--execute` only when those repository and GitHub side
effects are intended.

The parser accepts options in any order relative to the release level:

| Option | Default | Meaning |
| --- | --- | --- |
| `major`, `minor`, `patch` | `patch` | Release level (optional positional argument) |
| `--execute` | off | Apply changes instead of simulating them |
| `--project-file PATH` | `pyproject.toml` | PEP 621 project metadata file |
| `--changelog-file PATH` | `CHANGELOG.md` | Changelog file |
| `--cliff-config-file PATH` | `cliff.toml` | `git-cliff` configuration file |
| `--base-branch NAME` | `main` | Base branch for release operations and the PR |
| `--remote NAME` | `origin` | Git remote used for release operations |
| `--release-branch-prefix PREFIX` | `release/v` | Prefix for release branch names |

For example, this invocation uses a non-default project layout while remaining a
dry run:

```bash
forging-releases \
  --project-file config/pyproject.toml \
  --changelog-file docs/CHANGELOG.md \
  --cliff-config-file config/cliff.toml \
  --base-branch trunk \
  --remote upstream \
  --release-branch-prefix maintenance/release/ \
  minor
```

The same interface is available as a module:

```bash
python -m forging_releases.presentation --help
```

## Python import boundaries and extension points

Application code depends on ports rather than on Git or GitHub command details.
Use these stable imports for integrations and custom composition roots:

```python
from forging_releases.application.ports.outbound import (
    CommandRunner,
    PullRequestService,
    VersionControl,
)
from forging_releases.infrastructure import ReleaseConfiguration
```

`VersionControl` defines repository operations such as branch existence checks,
checkout, branch creation and deletion, commits, and pushes. `PullRequestService`
accepts a `ReleasePullRequest` and returns an `OpenPullRequestOutput`. `CommandRunner`
is the generic boundary for running external commands and is not Git-specific.
Application and presentation modules must not invoke `git`, `git-cliff`, or `gh`
directly.

The default composition root is `Container`. It wires:

- `GitVersionControl` from
  `forging_releases.infrastructure.vcs.git.git_version_control`;
- `GitHubCliPullRequestService` from
  `forging_releases.infrastructure.github.github_cli_pull_request_service`;
- `GitCliffChangelogGenerator` for changelog generation; and
- `SubprocessCommandRunner` from
  `forging_releases.infrastructure.commons.process` for external commands.

Pass a `ReleaseConfiguration` to `Container` when the project uses non-default
paths or branch names:

```python
from pathlib import Path

from forging_releases.infrastructure import ReleaseConfiguration
from forging_releases.infrastructure.container import Container

configuration = ReleaseConfiguration(
    project_file=Path("config/pyproject.toml"),
    changelog_file=Path("docs/CHANGELOG.md"),
    cliff_config_file=Path("config/cliff.toml"),
    base_branch="trunk",
    remote="upstream",
    release_branch_prefix="maintenance/release/",
)
container = Container(configuration)
```

To provide another VCS or pull-request provider, implement the existing
`VersionControl` or `PullRequestService` port, respectively, and select that
implementation in your composition root. Keep provider-specific process calls and
error translation inside the adapter; do not add them to application services or
presentation code. A custom provider may also implement `CommandRunner`, or use a
separate transport, without changing the release use cases.

## Build and safe installation verification

Build the wheel without a sibling source checkout or local `uv` source override:

```bash
rm -rf /tmp/forging-releases-smoke
mkdir -p /tmp/forging-releases-smoke
uv build --out-dir /tmp/forging-releases-smoke
python3.14 -m venv /tmp/forging-releases-smoke/venv
/tmp/forging-releases-smoke/venv/bin/pip install \
  /tmp/forging-releases-smoke/forging_releases-*.whl
/tmp/forging-releases-smoke/venv/bin/forging-releases --help
/tmp/forging-releases-smoke/venv/bin/python -m forging_releases.presentation --help
```

For a non-mutating fixture check, create a temporary PEP 621 project containing
`pyproject.toml`, `CHANGELOG.md`, and `cliff.toml`, initialize local Git history,
and run the installed command with the six configuration options above but without
`--execute`. Record the version file, changelog, branch list, and tags before and
after; they must be identical.

During verification, build and install locally only. Do not publish a package to an
index, create a GitHub release, or open an external pull request.
