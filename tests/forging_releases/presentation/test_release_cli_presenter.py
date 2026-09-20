from argparse import Namespace
from pathlib import Path
from typing import cast

import pytest

from forging_releases.application.errors.change_log_generation_error import ChangelogGenerationError
from forging_releases.application.ports.inbound.prepare_release_use_case import (
    PrepareReleaseInput,
    PrepareReleaseOutput,
)
from forging_releases.domain.errors.invalid_release_version_error import InvalidReleaseVersionError
from forging_releases.infrastructure.configuration import ReleaseConfiguration
from forging_releases.presentation.parsers.release_cli_parser import ReleaseCliParser
from forging_releases.presentation.presenters import (
    ContainerFactory,
    ReleaseCliPresenter,
)


class RecordingUseCase:
    def __init__(self, events: list[str]) -> None:
        self._events = events
        self.request: PrepareReleaseInput | None = None

    async def execute(self, request: PrepareReleaseInput) -> PrepareReleaseOutput:
        self._events.append("execute")
        self.request = request
        return PrepareReleaseOutput(
            version="1.2.3",
            branch="release/v1.2.3",
            tag="v1.2.3",
        )


class RecordingContainer:
    def __init__(self, events: list[str], use_case: RecordingUseCase) -> None:
        self._events = events
        self._use_case = use_case

    async def initialize(self) -> None:
        self._events.append("initialize")

    def get_prepare_release_use_case(self) -> RecordingUseCase:
        self._events.append("get_use_case")
        return self._use_case


def _factory_for(container: RecordingContainer) -> ContainerFactory:
    def factory(_configuration: ReleaseConfiguration) -> RecordingContainer:
        return container

    return cast(ContainerFactory, factory)


@pytest.mark.unit
class TestReleaseCliPresenter:
    async def test_present_initializes_before_getting_and_invoking_use_case(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        events: list[str] = []
        use_case = RecordingUseCase(events)
        container = RecordingContainer(events, use_case)
        configurations: list[ReleaseConfiguration] = []

        def factory(configuration: ReleaseConfiguration) -> object:
            configurations.append(configuration)
            return container

        presenter = ReleaseCliPresenter(
            parser=ReleaseCliParser(),
            container_factory=cast(ContainerFactory, factory),
        )

        await presenter.present(
            [
                "minor",
                "--project-file", "project.toml",
                "--changelog-file", "notes.md",
                "--cliff-config-file", "cliff-release.toml",
                "--base-branch", "trunk",
                "--remote", "upstream",
                "--release-branch-prefix", "stable/",
            ]
        )

        assert events == ["initialize", "get_use_case", "execute"]
        assert use_case.request == PrepareReleaseInput(level="minor", dry_run=True)
        assert configurations == [
            ReleaseConfiguration(
                project_file=Path("project.toml"),
                changelog_file=Path("notes.md"),
                cliff_config_file=Path("cliff-release.toml"),
                base_branch="trunk",
                remote="upstream",
                release_branch_prefix="stable/",
            )
        ]
        assert capsys.readouterr().out.splitlines() == [
            "Version:    1.2.3",
            "[DRY-RUN] No changes applied. Use --execute to apply.",
        ]

    async def test_present_execute_flag_disables_dry_run(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        events: list[str] = []
        use_case = RecordingUseCase(events)
        container = RecordingContainer(events, use_case)

        presenter = ReleaseCliPresenter(
            parser=ReleaseCliParser(),
            container_factory=_factory_for(container),
        )

        await presenter.present(["--execute", "patch"])

        assert use_case.request == PrepareReleaseInput(level="patch", dry_run=False)
        assert capsys.readouterr().out == "Version:    1.2.3\n"

    async def test_present_passes_configuration_to_factory_with_namespace_parser(self) -> None:
        events: list[str] = []
        use_case = RecordingUseCase(events)
        container = RecordingContainer(events, use_case)

        class FixedParser:
            def parse(self, _argv: list[str] | None = None) -> Namespace:
                return Namespace(
                    level="major",
                    execute=False,
                    project_file=Path("a.toml"),
                    changelog_file=Path("b.md"),
                    cliff_config_file=Path("c.toml"),
                    base_branch="develop",
                    remote="fork",
                    release_branch_prefix="release/",
                )

        configurations: list[ReleaseConfiguration] = []

        def factory(configuration: ReleaseConfiguration) -> object:
            configurations.append(configuration)
            return container

        presenter = ReleaseCliPresenter(
            parser=cast(ReleaseCliParser, FixedParser()),
            container_factory=cast(ContainerFactory, factory),
        )

        await presenter.present([])

        assert configurations == [
            ReleaseConfiguration(
                project_file=Path("a.toml"),
                changelog_file=Path("b.md"),
                cliff_config_file=Path("c.toml"),
                base_branch="develop",
                remote="fork",
                release_branch_prefix="release/",
            )
        ]

    async def test_present_prints_exact_expected_error_message(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        class FailingUseCase(RecordingUseCase):
            async def execute(self, request: PrepareReleaseInput) -> PrepareReleaseOutput:
                raise ChangelogGenerationError("git-cliff failed")

        events: list[str] = []
        container = RecordingContainer(events, FailingUseCase(events))
        presenter = ReleaseCliPresenter(
            parser=ReleaseCliParser(),
            container_factory=_factory_for(container),
        )

        error = ChangelogGenerationError("git-cliff failed")
        with pytest.raises(SystemExit) as raised:
            await presenter.present([])

        assert raised.value.code == 1
        assert capsys.readouterr().out == f"{error}\n"

    async def test_present_does_not_swallow_unexpected_errors(self) -> None:
        class FailingUseCase(RecordingUseCase):
            async def execute(self, request: PrepareReleaseInput) -> PrepareReleaseOutput:
                raise RuntimeError("unexpected failure")

        events: list[str] = []
        container = RecordingContainer(events, FailingUseCase(events))
        presenter = ReleaseCliPresenter(
            parser=ReleaseCliParser(),
            container_factory=_factory_for(container),
        )

        with pytest.raises(RuntimeError, match="unexpected failure"):
            await presenter.present([])

    async def test_present_prints_exact_invalid_version_error_message(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        class FailingUseCase(RecordingUseCase):
            async def execute(self, request: PrepareReleaseInput) -> PrepareReleaseOutput:
                raise InvalidReleaseVersionError("0.0.0")

        events: list[str] = []
        container = RecordingContainer(events, FailingUseCase(events))
        presenter = ReleaseCliPresenter(
            parser=ReleaseCliParser(),
            container_factory=_factory_for(container),
        )

        error = InvalidReleaseVersionError("0.0.0")
        with pytest.raises(SystemExit) as raised:
            await presenter.present([])

        assert raised.value.code == 1
        assert capsys.readouterr().out == f"{error}\n"
