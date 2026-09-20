# pyright: reportPrivateUsage=false
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from forging_releases.application.ports.inbound import PrepareReleaseInput
from forging_releases.application.ports.outbound import (
    ChangelogGenerator,
    ChangelogResponse,
    OpenPullRequestOutput,
    PullRequestService,
    VersionControl,
    VersioningService,
)
from forging_releases.application.services.open_release_pull_request_service import (
    OpenReleasePullRequestService,
)
from forging_releases.application.services.prepare_release_service import (
    PrepareReleaseService,
)
from forging_releases.domain.value_objects import ReleaseVersion
from forging_releases.infrastructure.configuration import ReleaseConfiguration
from forging_releases.infrastructure.container import Container


@pytest.mark.unit
class TestContainer:
    async def test_prepare_release_use_case_factory(self) -> None:
        container = Container()
        await container.initialize()
        use_case = container.get_prepare_release_use_case()

        assert isinstance(use_case, PrepareReleaseService)

    def test_open_release_pull_request_use_case_factory(self) -> None:
        container = Container()
        use_case = container.get_open_release_pull_request_use_case()

        assert isinstance(use_case, OpenReleasePullRequestService)

    async def test_configuration_resolves_relative_paths_and_wires_adapter_settings(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        configuration = ReleaseConfiguration(
            project_file=Path("config/project.toml"),
            changelog_file=Path("docs/releases.md"),
            cliff_config_file=Path("config/cliff.toml"),
            base_branch="trunk",
            remote="upstream",
            release_branch_prefix="stable/",
        )

        container = Container(configuration)

        assert container._versioning_service._pyproject_path == (
            tmp_path / "config/project.toml"
        )
        assert container._changelog_generator._changelog_path == (
            tmp_path / "docs/releases.md"
        )
        assert container._changelog_generator._cliff_config_path == (
            tmp_path / "config/cliff.toml"
        )
        assert container._version_control._base_branch == "trunk"
        assert container._version_control._remote == "upstream"
        assert container._version_control._release_branch_prefix == "stable/"
        await container.initialize()
        prepare_use_case = container.get_prepare_release_use_case()
        open_use_case = container.get_open_release_pull_request_use_case()
        assert prepare_use_case._release_branch_prefix == "stable/"
        assert open_use_case._base_branch == "trunk"
        assert open_use_case._release_branch_prefix == "stable/"

    async def test_initialized_workflow_uses_configured_base_and_branch_prefix(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        configuration = ReleaseConfiguration(
            project_file=Path("project.toml"),
            changelog_file=Path("releases.md"),
            cliff_config_file=Path("cliff.toml"),
            base_branch="trunk",
            remote="upstream",
            release_branch_prefix="stable/",
        )
        container = Container(configuration)

        versioning_service = Mock(spec=VersioningService)
        versioning_service.current_version.return_value = ReleaseVersion(1, 0, 0)
        versioning_service.compute_next_version.return_value = ReleaseVersion(1, 1, 0)
        version_control = Mock(spec=VersionControl)
        version_control.branch_exists.return_value = False
        changelog_generator = Mock(spec=ChangelogGenerator)
        changelog_generator.generate = AsyncMock(
            return_value=ChangelogResponse(entries=[]),
        )
        pull_request_service = Mock(spec=PullRequestService)
        pull_request_service.open.return_value = OpenPullRequestOutput(
            pr_id="42",
            url="https://github.com/org/repo/pull/42",
        )
        container._versioning_service = versioning_service
        container._version_control = version_control
        container._changelog_generator = changelog_generator
        container._pull_request_service = pull_request_service

        await container.initialize()
        use_case = container.get_prepare_release_use_case()
        result = await use_case.execute(
            PrepareReleaseInput(level="minor", dry_run=False),
        )

        assert result.branch == "stable/1.1.0"
        pull_request = pull_request_service.open.call_args.args[0]
        assert pull_request.base == "trunk"
        assert pull_request.head.value == "stable/1.1.0"

    def test_configuration_defaults_match_release_workflow(self) -> None:
        assert ReleaseConfiguration() == ReleaseConfiguration(
            project_file=Path("pyproject.toml"),
            changelog_file=Path("CHANGELOG.md"),
            cliff_config_file=Path("cliff.toml"),
            base_branch="main",
            remote="origin",
            release_branch_prefix="release/v",
        )
