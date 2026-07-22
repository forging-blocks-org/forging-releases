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
from forging_releases.infrastructure.commons.process import SubprocessCommandRunner
from forging_releases.infrastructure.git.git_version_control import GitVersionControl
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


class Container:
    """Composition root."""

    def __init__(self) -> None:
        from pathlib import Path

        self._command_runner = SubprocessCommandRunner()
        self._versioning_service = PyProjectVersioningService(
            Path.cwd() / "pyproject.toml"
        )
        self._version_control = GitVersionControl(self._command_runner)
        self._changelog_generator = GitCliffChangelogGenerator(self._command_runner)
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
        )

    def get_open_release_pull_request_use_case(self) -> OpenReleasePullRequestService:
        """Creates open release pull request use case."""
        return OpenReleasePullRequestService(
            pull_request_service=self._pull_request_service,
        )

    async def _setup_message_handlers(self) -> None:
        """Register all events handlers"""
        self._message_bus = InMemoryReleaseCommandBus()
        open_pull_request_service = OpenReleasePullRequestService(
            pull_request_service=self._pull_request_service,
        )
        open_pull_request_handler = OpenPullRequestHandler(open_pull_request_service)

        await self._message_bus.register(OpenPullRequestCommand, open_pull_request_handler)
