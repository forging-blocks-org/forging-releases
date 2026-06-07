from __future__ import annotations

from forging_releases.application.ports.inbound import (
    OpenReleasePullRequestUseCase,
    PrepareReleaseUseCase,
)
from forging_releases.application.ports.outbound import (
    ChangelogGenerator,
    PullRequestService,
    ReleaseCommandBus,
    ReleaseTransaction,
    VersionControl,
    VersioningService,
)
from forging_releases.application.services.open_release_pull_request_service import (
    OpenReleasePullRequestService,
)
from forging_releases.application.services.prepare_release_service import (
    PrepareReleaseService,
)
from forging_releases.domain.commands import OpenPullRequestCommand
from forging_releases.infrastructure.changelog_generator.git_changelog_generator import (
    GitChangelogGenerator,
)
from forging_releases.infrastructure.command_bus.in_memory_release_command_bus import (
    InMemoryReleaseCommandBus,
)
from forging_releases.infrastructure.handler.open_pull_request_handler import (
    OpenPullRequestHandler,
)
from forging_releases.infrastructure.pull_request_service.github_pull_request_service import (
    GitHubPullRequestService,
)
from forging_releases.infrastructure.release_transaction.in_memory_release_transaction import (
    InMemoryReleaseTransaction,
)
from forging_releases.infrastructure.version_control.git_version_control import (
    GitVersionControl,
)
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


class Container:
    def __init__(
        self,
        *,
        cwd: str | None = None,
        main_branch: str = "main",
        github_owner: str | None = None,
        github_repo: str | None = None,
        github_token: str | None = None,
        github_base_url: str = "https://api.github.com",
    ) -> None:
        self._cwd = cwd
        self._main_branch = main_branch
        self._github_owner = github_owner
        self._github_repo = github_repo
        self._github_token = github_token
        self._github_base_url = github_base_url

        self._versioning_service: VersioningService | None = None
        self._version_control: VersionControl | None = None
        self._transaction: ReleaseTransaction | None = None
        self._message_bus: ReleaseCommandBus[OpenPullRequestCommand] | None = None
        self._changelog_generator: ChangelogGenerator | None = None
        self._pull_request_service: PullRequestService | None = None
        self._prepare_use_case: PrepareReleaseUseCase | None = None
        self._open_pr_use_case: OpenReleasePullRequestUseCase | None = None

    def get_prepare_release_use_case(self) -> PrepareReleaseUseCase:
        if self._prepare_use_case is None:
            self._prepare_use_case = PrepareReleaseService(
                versioning_service=self._resolve_versioning_service(),
                version_control=self._resolve_version_control(),
                transaction=self._resolve_transaction(),
                message_bus=self._resolve_message_bus(),
                changelog_generator=self._resolve_changelog_generator(),
            )
        return self._prepare_use_case

    def get_open_release_pull_request_use_case(self) -> OpenReleasePullRequestUseCase:
        if self._open_pr_use_case is None:
            self._open_pr_use_case = OpenReleasePullRequestService(
                pull_request_service=self._resolve_pull_request_service(),
            )
        return self._open_pr_use_case

    async def initialize(self) -> None:
        if self._github_owner is None or self._github_repo is None or self._github_token is None:
            return

        handler = OpenPullRequestHandler(
            use_case=self.get_open_release_pull_request_use_case(),
        )
        bus = self._resolve_message_bus()
        await bus.register(OpenPullRequestCommand, handler)

    def _resolve_versioning_service(self) -> VersioningService:
        if self._versioning_service is None:
            self._versioning_service = PyProjectVersioningService(cwd=self._cwd)
        return self._versioning_service

    def _resolve_version_control(self) -> VersionControl:
        if self._version_control is None:
            self._version_control = GitVersionControl(
                cwd=self._cwd,
                main_branch=self._main_branch,
            )
        return self._version_control

    def _resolve_transaction(self) -> ReleaseTransaction:
        if self._transaction is None:
            self._transaction = InMemoryReleaseTransaction()
        return self._transaction

    def _resolve_message_bus(self) -> ReleaseCommandBus[OpenPullRequestCommand]:
        if self._message_bus is None:
            self._message_bus = InMemoryReleaseCommandBus[OpenPullRequestCommand]()
        return self._message_bus

    def _resolve_changelog_generator(self) -> ChangelogGenerator:
        if self._changelog_generator is None:
            self._changelog_generator = GitChangelogGenerator(cwd=self._cwd)
        return self._changelog_generator

    def _resolve_pull_request_service(self) -> PullRequestService:
        if self._pull_request_service is None:
            self._pull_request_service = GitHubPullRequestService(
                owner=self._github_owner or "",
                repo=self._github_repo or "",
                token=self._github_token or "",
                base_url=self._github_base_url,
            )
        return self._pull_request_service
