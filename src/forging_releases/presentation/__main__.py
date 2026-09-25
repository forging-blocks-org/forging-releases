import asyncio
from collections.abc import Sequence

from forging_releases.infrastructure.container import Container
from forging_releases.presentation.parsers.release_cli_parser import ReleaseCliParser
from forging_releases.presentation.presenters.release_cli_presenter import ReleaseCliPresenter


async def main(argv: Sequence[str] | None = None) -> None:
    container = Container()
    await container.initialize()

    parser = ReleaseCliParser()
    presenter = ReleaseCliPresenter(parser, container)
    await presenter.present(argv)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
