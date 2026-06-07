# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
from __future__ import annotations

import pytest

from forging_releases.application.ports.inbound import (
    OpenReleasePullRequestUseCase,
    PrepareReleaseUseCase,
)
from forging_releases.infrastructure.changelog_generator.git_changelog_generator import (
    GitChangelogGenerator,
)
from forging_releases.infrastructure.command_bus.in_memory_release_command_bus import (
    InMemoryReleaseCommandBus,
)
from forging_releases.infrastructure.container import Container
from forging_releases.infrastructure.release_transaction.in_memory_release_transaction import (
    InMemoryReleaseTransaction,
)
from forging_releases.infrastructure.version_control.git_version_control import GitVersionControl
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestContainer:
    async def test_get_prepare_release_use_case_when_called_then_returns_wired_instance(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        use_case = container_with_temp_repo.get_prepare_release_use_case()

        assert isinstance(use_case, PrepareReleaseUseCase)

    async def test_get_open_release_pull_request_use_case_when_called_then_returns_wired_instance(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        use_case = container_with_temp_repo.get_open_release_pull_request_use_case()

        assert isinstance(use_case, OpenReleasePullRequestUseCase)

    async def test_initialize_when_called_then_registers_handler_with_bus(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        await container_with_temp_repo.initialize()

        bus = container_with_temp_repo._resolve_message_bus()

        assert isinstance(bus, InMemoryReleaseCommandBus)

    async def test_get_prepare_release_use_case_when_called_multiple_then_returns_consistent_instances(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        use_case_a = container_with_temp_repo.get_prepare_release_use_case()
        use_case_b = container_with_temp_repo.get_prepare_release_use_case()

        assert use_case_a is use_case_b

    async def test_resolve_when_all_adapters_requested_then_returns_correct_instances(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        vc = container_with_temp_repo._resolve_version_control()
        vs = container_with_temp_repo._resolve_versioning_service()
        tx = container_with_temp_repo._resolve_transaction()
        cg = container_with_temp_repo._resolve_changelog_generator()

        assert isinstance(vc, GitVersionControl)
        assert isinstance(vs, PyProjectVersioningService)
        assert isinstance(tx, InMemoryReleaseTransaction)
        assert isinstance(cg, GitChangelogGenerator)
