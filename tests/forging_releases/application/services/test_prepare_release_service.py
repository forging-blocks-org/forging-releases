# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
from unittest.mock import AsyncMock, Mock

import pytest

from forging_releases.domain.errors import InvalidReleaseLevelError
from forging_releases.application.ports.inbound.prepare_release_use_case import (
    PrepareReleaseInput,
)
from forging_releases.application.ports.outbound.changelog_generator import (
    ChangelogGenerator,
    ChangelogResponse,
)
from forging_releases.application.ports.outbound.release_command_bus import ReleaseCommandBus
from forging_releases.application.ports.outbound.release_transaction import ReleaseTransaction
from forging_releases.application.ports.outbound.version_control import VersionControl
from forging_releases.application.ports.outbound.versioning_service import VersioningService
from forging_releases.application.services.prepare_release_service import (
    PrepareReleaseService,
)
from forging_releases.domain.value_objects import (
    ReleaseBranchName,
    ReleaseVersion,
)


def _make_version(major: int, minor: int, patch: int) -> ReleaseVersion:
    return ReleaseVersion(major, minor, patch)


def _make_branch(version: ReleaseVersion) -> ReleaseBranchName:
    return ReleaseBranchName(f"release/v{version.value}")


def _make_transaction_mock() -> Mock:
    transaction = Mock(spec=ReleaseTransaction)
    transaction.__aenter__ = AsyncMock(return_value=transaction)
    transaction.__aexit__ = AsyncMock(return_value=None)
    return transaction


def _make_message_bus_mock() -> Mock:
    message_bus = Mock(spec=ReleaseCommandBus)
    message_bus.send = AsyncMock()
    return message_bus


@pytest.mark.unit
class TestPrepareReleaseServiceDryRun:
    """Tests for the dry_run=True path."""

    async def test_execute_when_dry_run_then_returns_ok_with_output(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)

        current = _make_version(1, 0, 0)
        next_version = _make_version(1, 1, 0)

        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = False
        changelog_generator.generate = AsyncMock(
            return_value=ChangelogResponse(entries=["- feat: something"])
        )

        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )

        request = PrepareReleaseInput(level="minor", dry_run=True)

        result = await service.execute(request)  # type: ignore[reportArgumentType]

        assert result.version == "1.1.0"
        assert result.branch == "release/v1.1.0"
        assert result.tag == "v1.1.0"
        assert result.changelog_entries == ["- feat: something"]
        message_bus.send.assert_not_called()

    async def test_execute_when_dry_run_branch_exists_then_checkout_not_create(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)

        current = _make_version(1, 0, 0)
        next_version = _make_version(1, 0, 1)
        branch = _make_branch(next_version)

        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = True
        changelog_generator.generate = AsyncMock(return_value=ChangelogResponse(entries=[]))

        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )

        request = PrepareReleaseInput(level="patch", dry_run=True)

        await service.execute(request)  # type: ignore[reportArgumentType]

        version_control.checkout.assert_called_once_with(branch, dry_run=True)
        version_control.create_branch.assert_not_called()


@pytest.mark.unit
class TestPrepareReleaseServiceNormal:
    async def test_execute_when_new_branch_then_creates_and_pushes(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        current = _make_version(1, 0, 0)
        next_version = _make_version(2, 0, 0)
        branch = _make_branch(next_version)
        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = False
        changelog_generator.generate = AsyncMock(
            return_value=ChangelogResponse(entries=["- feat: major release"])
        )
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="major", dry_run=False)
        result = await service.execute(request)  # type: ignore[reportArgumentType]
        assert result.version == "2.0.0"
        assert result.branch == "release/v2.0.0"
        assert result.tag == "v2.0.0"
        assert result.changelog_entries == ["- feat: major release"]
        version_control.create_branch.assert_called_once_with(branch, dry_run=False)
        version_control.checkout.assert_not_called()
        version_control.push.assert_called_once_with(branch)
        message_bus.send.assert_called_once()

    async def test_execute_when_branch_exists_then_checkout_and_push(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        current = _make_version(1, 0, 0)
        next_version = _make_version(1, 0, 1)
        branch = _make_branch(next_version)
        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = True
        changelog_generator.generate = AsyncMock(return_value=ChangelogResponse(entries=[]))
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="patch", dry_run=False)
        await service.execute(request)  # type: ignore[reportArgumentType]
        version_control.checkout.assert_called_once_with(branch, dry_run=False)
        version_control.create_branch.assert_not_called()

    async def test_execute_when_not_dry_run_then_commits_artifacts(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        current = _make_version(1, 0, 0)
        next_version = _make_version(1, 0, 1)
        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = False
        changelog_generator.generate = AsyncMock(return_value=ChangelogResponse(entries=[]))
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="patch", dry_run=False)
        await service.execute(request)  # type: ignore[reportArgumentType]
        version_control.commit_release_artifacts.assert_called_once()


@pytest.mark.unit
class TestPrepareReleaseServiceValueComputation:
    async def test_execute_when_patch_level_then_computes_patch_bump(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        current = _make_version(1, 2, 3)
        next_version = _make_version(1, 2, 4)
        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = False
        changelog_generator.generate = AsyncMock(return_value=ChangelogResponse(entries=[]))
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="patch", dry_run=True)
        result = await service.execute(request)  # type: ignore[reportArgumentType]
        assert result.version == "1.2.4"

    async def test_execute_when_major_level_then_computes_major_bump(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        current = _make_version(1, 2, 3)
        next_version = _make_version(2, 0, 0)
        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = False
        changelog_generator.generate = AsyncMock(return_value=ChangelogResponse(entries=[]))
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="major", dry_run=True)
        result = await service.execute(request)  # type: ignore[reportArgumentType]
        assert result.version == "2.0.0"

    async def test_execute_when_minor_level_then_computes_minor_bump(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        current = _make_version(1, 2, 3)
        next_version = _make_version(1, 3, 0)
        versioning_service.current_version.return_value = current
        versioning_service.compute_next_version.return_value = next_version
        version_control.branch_exists.return_value = False
        changelog_generator.generate = AsyncMock(return_value=ChangelogResponse(entries=[]))
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="minor", dry_run=True)
        result = await service.execute(request)  # type: ignore[reportArgumentType]
        assert result.version == "1.3.0"


@pytest.mark.unit
class TestPrepareReleaseServiceErrorPath:
    async def test_execute_when_invalid_release_level_then_returns_err(self) -> None:
        versioning_service = Mock(spec=VersioningService)
        version_control = Mock(spec=VersionControl)
        transaction = _make_transaction_mock()
        message_bus = _make_message_bus_mock()
        changelog_generator = Mock(spec=ChangelogGenerator)
        service = PrepareReleaseService(
            versioning_service=versioning_service,
            version_control=version_control,
            transaction=transaction,
            message_bus=message_bus,
            changelog_generator=changelog_generator,
        )
        request = PrepareReleaseInput(level="invalid", dry_run=True)
        with pytest.raises(InvalidReleaseLevelError) as exc_info:
            await service.execute(request)  # type: ignore[reportArgumentType]
        assert "invalid" in str(exc_info.value)
