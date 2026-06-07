# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import pytest

from forging_releases.application.ports.inbound import (
    OpenReleasePullRequestUseCase,
    PrepareReleaseUseCase,
)
from forging_releases.infrastructure.changelog_generator.changelog_generator import (
    GitChangelogGenerator,
)
from forging_releases.infrastructure.command_bus.command_bus import (
    InMemoryReleaseCommandBus,
)
from forging_releases.infrastructure.container import Container
from forging_releases.infrastructure.release_transaction.release_transaction import (
    InMemoryReleaseTransaction,
)
from forging_releases.infrastructure.version_control.version_control import GitVersionControl
from forging_releases.infrastructure.versioning_service.versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestContainerWiring:
    async def test_get_prepare_release_use_case_returns_wired_instance(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        use_case = container_with_temp_repo.get_prepare_release_use_case()
        assert isinstance(use_case, PrepareReleaseUseCase)

    async def test_get_open_release_pull_request_use_case_returns_wired_instance(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        use_case = container_with_temp_repo.get_open_release_pull_request_use_case()
        assert isinstance(use_case, OpenReleasePullRequestUseCase)

    async def test_initialize_registers_handler_with_bus(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        await container_with_temp_repo.initialize()

        bus = container_with_temp_repo._resolve_message_bus()
        assert isinstance(bus, InMemoryReleaseCommandBus)

    async def test_container_returns_consistent_instances(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        use_case_a = container_with_temp_repo.get_prepare_release_use_case()
        use_case_b = container_with_temp_repo.get_prepare_release_use_case()
        assert use_case_a is use_case_b

    async def test_all_adapters_can_be_resolved(
        self,
        container_with_temp_repo: Container,
    ) -> None:
        vc = container_with_temp_repo._resolve_version_control()
        assert isinstance(vc, GitVersionControl)

        vs = container_with_temp_repo._resolve_versioning_service()
        assert isinstance(vs, PyProjectVersioningService)

        tx = container_with_temp_repo._resolve_transaction()
        assert isinstance(tx, InMemoryReleaseTransaction)

        cg = container_with_temp_repo._resolve_changelog_generator()
        assert isinstance(cg, GitChangelogGenerator)
