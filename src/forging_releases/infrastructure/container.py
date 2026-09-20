from pathlib import Path

from forging_releases.application.services.open_release_pull_request_service import (
    OpenReleasePullRequestService,
)
from forging_releases.application.services.prepare_release_service import (
    PrepareReleaseService,
)
from forging_releases.domain.commands.open_pull_request_command import (
    OpenPullRequestCommand,
)
from forging_releases.infrastructure.bus.in_memory_release_command_bus import (
    InMemoryReleaseCommandBus,
)
from forging_releases.infrastructure.changelog.git_cliff_changelog_generator import (
    GitCliffChangelogGenerator,
)
from forging_releases.application.ports.outbound import CommandRunner
from forging_releases.infrastructure.commons.process import SubprocessCommandRunner
from forging_releases.infrastructure.configuration import ReleaseConfiguration
from forging_releases.infrastructure.vcs.git.git_version_control import GitVersionControl
from forging_releases.infrastructure.github.github_cli_pull_request_service import (
    GitHubCliPullRequestService,
)
from forging_releases.infrastructure.handlers import OpenPullRequestHandler
from forging_releases.infrastructure.transactions.in_memory_release_transaction import (
    InMemoryReleaseTransaction,
)
from forging_releases.infrastructure.versioning.pyproject_versioning_service import (
    PyProjectVersioningService,
)


def _resolve_path(path: Path, *, cwd: Path) -> Path:
    return path if path.is_absolute() else cwd / path


class Container:
    """Composition root."""

    def __init__(
        self,
        configuration: ReleaseConfiguration | None = None,
    ) -> None:
        configuration = configuration or ReleaseConfiguration()
        cwd = Path.cwd()
        project_file = _resolve_path(configuration.project_file, cwd=cwd)
        changelog_file = _resolve_path(configuration.changelog_file, cwd=cwd)
        cliff_config_file = _resolve_path(configuration.cliff_config_file, cwd=cwd)
        self._configuration: ReleaseConfiguration = configuration

        self._command_runner: CommandRunner = SubprocessCommandRunner()
        self._versioning_service = PyProjectVersioningService(project_file)
        self._version_control = GitVersionControl(
            self._command_runner,
            base_branch=configuration.base_branch,
            remote=configuration.remote,
            release_branch_prefix=configuration.release_branch_prefix,
        )
        self._changelog_generator = GitCliffChangelogGenerator(
            self._command_runner,
            changelog_path=changelog_file,
            cliff_config_path=cliff_config_file,
        )
        self._pull_request_service = GitHubCliPullRequestService(self._command_runner)
        self._message_bus: InMemoryReleaseCommandBus | None = None

    async def initialize(self) -> None:
        await self._setup_message_handlers()

    def get_prepare_release_use_case(self) -> PrepareReleaseService:
        """Creates new use case with fresh transaction/event bus."""
        if self._message_bus is None:
            raise RuntimeError("Container not initialized. Call .initialize() first.")

        return PrepareReleaseService(
            versioning_service=self._versioning_service,
            version_control=self._version_control,
            changelog_generator=self._changelog_generator,
            transaction=InMemoryReleaseTransaction(),
            message_bus=self._message_bus,
            release_branch_prefix=self._configuration.release_branch_prefix,
        )

    def get_open_release_pull_request_use_case(self) -> OpenReleasePullRequestService:
        """Creates open release pull request use case."""
        return OpenReleasePullRequestService(
            pull_request_service=self._pull_request_service,
            base_branch=self._configuration.base_branch,
            release_branch_prefix=self._configuration.release_branch_prefix,
        )

    async def _setup_message_handlers(self) -> None:
        """Register all events handlers"""
        self._message_bus = InMemoryReleaseCommandBus()
        open_pull_request_service = OpenReleasePullRequestService(
            pull_request_service=self._pull_request_service,
            base_branch=self._configuration.base_branch,
            release_branch_prefix=self._configuration.release_branch_prefix,
        )
        open_pull_request_handler = OpenPullRequestHandler(open_pull_request_service)

        await self._message_bus.register(OpenPullRequestCommand, open_pull_request_handler)
