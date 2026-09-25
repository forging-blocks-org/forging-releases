# forging-releases

Release automation CLI for Forging Blocks projects.

## Usage

The release CLI uses a parser/presenter presentation layer. Invoke it
through the installed console script or the package module.

```bash
forging-releases major|minor|patch [--execute]
```

- `major|minor|patch` selects the semantic version level to bump
  (default: `patch`).
- `--execute` applies real changes; without it the release runs as a
  dry-run simulation.

To run from a source checkout:

```bash
python -m forging_releases.presentation [major|minor|patch] [--execute]
```
