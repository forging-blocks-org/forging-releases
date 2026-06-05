# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false
from dataclasses import FrozenInstanceError

import pytest

from forging_releases.application.ports.inbound.prepare_release_use_case import (
    PrepareReleaseInput,
    PrepareReleaseOutput,
)


@pytest.mark.unit
class TestPrepareReleaseInput:
    def test_init_when_created_with_level_then_stores_value(self) -> None:
        request = PrepareReleaseInput(level="minor")

        assert request.level == "minor"
        assert request.dry_run is False

    def test_init_when_dry_run_true_then_stored(self) -> None:
        request = PrepareReleaseInput(level="patch", dry_run=True)

        assert request.dry_run is True

    def test_init_when_major_level_then_stored(self) -> None:
        request = PrepareReleaseInput(level="major")

        assert request.level == "major"

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        request = PrepareReleaseInput(level="minor")

        with pytest.raises(FrozenInstanceError):
            request.level = "major"  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        r1 = PrepareReleaseInput(level="patch")
        r2 = PrepareReleaseInput(level="patch")

        assert r1 == r2

    def test_eq_when_different_level_then_not_equal(self) -> None:
        r1 = PrepareReleaseInput(level="patch")
        r2 = PrepareReleaseInput(level="minor")

        assert r1 != r2


@pytest.mark.unit
class TestPrepareReleaseOutput:
    def test_init_when_created_with_all_fields_then_stores_all(self) -> None:
        output = PrepareReleaseOutput(
            version="1.2.3",
            branch="release/v1.2.3",
            tag="v1.2.3",
            changelog_entries=["- feat: new feature", "- fix: bug fix"],
        )

        assert output.version == "1.2.3"
        assert output.branch == "release/v1.2.3"
        assert output.tag == "v1.2.3"
        assert output.changelog_entries == ["- feat: new feature", "- fix: bug fix"]

    def test_init_when_changelog_entries_default_then_empty_list(self) -> None:
        output = PrepareReleaseOutput(
            version="1.0.0",
            branch="release/v1.0.0",
            tag="v1.0.0",
        )

        assert output.changelog_entries == []

    def test_init_when_frozen_then_cannot_modify(self) -> None:
        output = PrepareReleaseOutput(
            version="1.0.0",
            branch="release/v1.0.0",
            tag="v1.0.0",
        )

        with pytest.raises(FrozenInstanceError):
            output.version = "2.0.0"  # type: ignore[misc]

    def test_eq_when_same_values_then_equal(self) -> None:
        o1 = PrepareReleaseOutput(
            version="1.0.0",
            branch="release/v1.0.0",
            tag="v1.0.0",
            changelog_entries=["- feat: x"],
        )
        o2 = PrepareReleaseOutput(
            version="1.0.0",
            branch="release/v1.0.0",
            tag="v1.0.0",
            changelog_entries=["- feat: x"],
        )

        assert o1 == o2

    def test_eq_when_different_changelog_then_not_equal(self) -> None:
        o1 = PrepareReleaseOutput(
            version="1.0.0",
            branch="release/v1.0.0",
            tag="v1.0.0",
            changelog_entries=["- feat: x"],
        )
        o2 = PrepareReleaseOutput(
            version="1.0.0",
            branch="release/v1.0.0",
            tag="v1.0.0",
            changelog_entries=["- feat: y"],
        )

        assert o1 != o2
