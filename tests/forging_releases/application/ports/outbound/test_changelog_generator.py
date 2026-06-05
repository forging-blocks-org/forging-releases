# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
from dataclasses import FrozenInstanceError

import pytest

from forging_releases.application.ports.outbound.changelog_generator import (
    ChangelogRequest,
    ChangelogResponse,
)


@pytest.mark.unit
class TestChangelogRequest:
    def test_init_when_created_with_from_version_then_stores_values(self) -> None:
        request = ChangelogRequest(from_version="1.0.0")

        assert request.from_version == "1.0.0"
        assert request.dry_run is False

    def test_init_when_dry_run_true_then_stored(self) -> None:
        request = ChangelogRequest(from_version="1.0.0", dry_run=True)

        assert request.dry_run is True

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        request = ChangelogRequest(from_version="1.0.0")

        with pytest.raises(FrozenInstanceError):
            request.from_version = "2.0.0"  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        r1 = ChangelogRequest(from_version="1.0.0")
        r2 = ChangelogRequest(from_version="1.0.0")

        assert r1 == r2

    def test_eq_when_different_version_then_not_equal(self) -> None:
        r1 = ChangelogRequest(from_version="1.0.0")
        r2 = ChangelogRequest(from_version="2.0.0")

        assert r1 != r2


@pytest.mark.unit
class TestChangelogResponse:
    def test_init_when_created_with_entries_then_stores_all(self) -> None:
        entries = ["- feat: add login", "- fix: bug"]
        response = ChangelogResponse(entries=entries)

        assert response.entries == entries

    def test_init_when_created_with_empty_entries_then_stores_empty(self) -> None:
        response = ChangelogResponse(entries=[])

        assert response.entries == []

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        response = ChangelogResponse(entries=["- feat: x"])

        with pytest.raises(FrozenInstanceError):
            response.entries = []  # type: ignore[misc]

    def test_eq_when_same_entries_then_equal(self) -> None:
        r1 = ChangelogResponse(entries=["- feat: x"])
        r2 = ChangelogResponse(entries=["- feat: x"])

        assert r1 == r2

    def test_eq_when_different_entries_then_not_equal(self) -> None:
        r1 = ChangelogResponse(entries=["- feat: x"])
        r2 = ChangelogResponse(entries=["- feat: y"])

        assert r1 != r2
