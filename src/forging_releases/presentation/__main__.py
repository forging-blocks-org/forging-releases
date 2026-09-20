"""Synchronous entrypoint for the forging-releases command-line interface."""

import asyncio
from collections.abc import Sequence

from forging_releases.infrastructure.configuration import ReleaseConfiguration
from forging_releases.infrastructure.container import Container
from forging_releases.presentation.parsers import ReleaseCliParser
from forging_releases.presentation.presenters import ReleaseCliPresenter


def _container_factory(configuration: ReleaseConfiguration) -> Container:
    """Build the production composition root from CLI configuration."""
    return Container(configuration)


def main(argv: Sequence[str] | None = None) -> None:
    """Run the asynchronous release workflow from a synchronous console script."""
    parser = ReleaseCliParser()
    presenter = ReleaseCliPresenter(parser, _container_factory)
    asyncio.run(presenter.present(argv))


if __name__ == "__main__":
    main()
