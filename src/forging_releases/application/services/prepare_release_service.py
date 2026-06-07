from forging_blocks.foundation import Err, Ok, Result

from forging_releases.application.errors import (
    CommandExecutionError,
    InvalidReleaseLevelValueError,
    VersionNotFoundError,
)
from forging_releases.application.ports.inbound import (
    PrepareReleaseInput,
    PrepareReleaseOutput,
    PrepareReleaseUseCase,
)
from forging_releases.application.ports.outbound import (
    ChangelogGenerator,
    ChangelogRequest,
    ReleaseCommandBus,
    ReleaseTransaction,
    VersionControl,
    VersioningService,
)
from forging_releases.application.workflow import ReleaseContext, ReleaseStep
from forging_releases.domain.commands import OpenPullRequestCommand
from forging_releases.domain.value_objects import (
    ReleaseBranchName,
    ReleaseLevel,
    TagName,
)

type PrepareReleaseError = (
    InvalidReleaseLevelValueError | VersionNotFoundError | CommandExecutionError
)


class PrepareReleaseService(PrepareReleaseUseCase):
    """Service for preparing the release synchonosly and send a command to open a PR.

    Responsibilities:
    - calculate the next version
    - create a release branch
    - instantiate tag name
    - check if the branch already exists
    - prepare a release
    - check if its a dry run to avoid modifying the repo
    - delegate to infrastructure
    """

    def __init__(
        self,
        *,
        versioning_service: VersioningService,
        version_control: VersionControl,
        transaction: ReleaseTransaction,
        message_bus: ReleaseCommandBus[OpenPullRequestCommand],
        changelog_generator: ChangelogGenerator,
    ) -> None:
        self._versioning_service = versioning_service
        self._version_control = version_control
        self._transaction = transaction
        self._message_bus = message_bus
        self._changelog_generator = changelog_generator

    async def execute(
        self,
        request: PrepareReleaseInput,
    ) -> Result[PrepareReleaseOutput, PrepareReleaseError]:
        match ReleaseLevel.from_str(request.level):
            case Err():
                return Err(InvalidReleaseLevelValueError(request.level))
            case Ok(value=level):
                pass
            case _:
                return Err(InvalidReleaseLevelValueError(request.level))

        level = ReleaseLevel.from_str(request.level).value
        assert level is not None

        version_result = self._versioning_service.current_version()
        match version_result:
            case Err(error=err):
                return Err(err)
            case Ok(value=current_version):
                pass
            case _:
                return Err(VersionNotFoundError("unknown error"))

        current_version = version_result.value
        assert current_version is not None
        next_version = self._versioning_service.compute_next_version(level)

        branch = ReleaseBranchName.create(next_version)
        tag = TagName.create(next_version)

        branch_exists = self._version_control.branch_exists(branch)

        context = ReleaseContext(
            previous_version=current_version,
            version=next_version,
            branch=branch,
            tag=tag,
            branch_exists=branch_exists,
            dry_run=request.dry_run,
        )

        result = await self._prepare_release_transactionally(context)
        match result:
            case Err(error=err):
                return Err(err)
            case Ok(value=changelog_entries):
                pass
            case _:
                return Err(CommandExecutionError("release preparation", "unknown error"))

        changelog_entries = result.value
        if not context.dry_run:
            await self._send_command(context)

        return Ok(self._make_output(context, changelog_entries))

    def _make_output(
        self, context: ReleaseContext, changelog_entries: list[str]
    ) -> PrepareReleaseOutput:
        return PrepareReleaseOutput(
            version=context.version.value,
            branch=context.branch.value,
            tag=context.tag.value,
            changelog_entries=changelog_entries,
        )

    async def _send_command(self, context: ReleaseContext) -> None:
        command = OpenPullRequestCommand(
            version=context.version.value,
            branch=context.branch.value,
            dry_run=context.dry_run,
        )
        await self._message_bus.send(command)

    async def _prepare_release_transactionally(
        self,
        context: ReleaseContext,
    ) -> Result[list[str], CommandExecutionError]:
        if context.dry_run:
            return Ok(await self._prepare_release_dry_run(context))

        async with self._transaction:
            self._transaction.register_step(
                ReleaseStep(
                    name="checkout_main",
                    undo=lambda: self._version_control.checkout_main(),
                )
            )

            branch_result = self._branch_handling(context)
            match branch_result:
                case Err(error=err):
                    return Err(err)
                case _:
                    pass

            self._apply_version(context, dry_run=False)
            changelog_entries = await self._generate_changelog(context)

            commit_result = self._version_control.commit_release_artifacts()
            match commit_result:
                case Err(error=err):
                    return Err(err)
                case _:
                    pass

            push_result = self._push_branch(context)
            match push_result:
                case Err(error=err):
                    return Err(err)
                case _:
                    pass

        return Ok(changelog_entries)

    async def _prepare_release_dry_run(self, context: ReleaseContext) -> list[str]:
        self._branch_handling(context, dry_run=True)
        self._versioning_service.apply_version(context.version, dry_run=True)
        changelog_entries = await self._generate_changelog(context)
        self._version_control.commit_release_artifacts(dry_run=True)
        self._version_control.push(context.branch, dry_run=True)
        return changelog_entries

    def _branch_handling(
        self, context: ReleaseContext, *, dry_run: bool = False
    ) -> Result[None, CommandExecutionError]:
        if context.branch_exists:
            return self._version_control.checkout(context.branch, dry_run=dry_run)
        result = self._version_control.create_branch(context.branch, dry_run=dry_run)
        match result:
            case Err(error=err):
                return Err(err)
            case _:
                self._transaction.register_step(
                    ReleaseStep(
                        name="delete_local_branch",
                        undo=lambda: self._version_control.delete_local_branch(context.branch),
                    )
                )
                return Ok(None)

    def _apply_version(self, context: ReleaseContext, *, dry_run: bool = False) -> None:
        self._transaction.register_step(
            ReleaseStep(
                name="rollback_version",
                undo=lambda: self._versioning_service.rollback_version(context.previous_version),
            )
        )
        self._versioning_service.apply_version(context.version, dry_run=dry_run)

    async def _generate_changelog(self, context: ReleaseContext) -> list[str]:
        response = await self._changelog_generator.generate(
            ChangelogRequest(
                from_version=context.version.value,
                dry_run=context.dry_run,
            )
        )
        return response.entries

    def _push_branch(self, context: ReleaseContext) -> Result[None, CommandExecutionError]:
        self._transaction.register_step(
            ReleaseStep(
                name="delete_remote_branch",
                undo=lambda: self._version_control.delete_remote_branch(context.branch),
            )
        )

        return self._version_control.push(context.branch)
