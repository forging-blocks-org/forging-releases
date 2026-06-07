# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from pathlib import Path

import pytest
from .conftest import read_version

from forging_blocks.foundation import Ok

from forging_releases.domain.value_objects import ReleaseVersion
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestApplyVersion:
    def test_when_applied_then_pyproject_updated(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        new_version = ReleaseVersion(2, 0, 0)
        svc.apply_version(new_version)
        assert read_version(str(Path(temp_pyproject_dir) / "pyproject.toml")) == "2.0.0"

    def test_when_dry_run_then_pyproject_not_modified(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        new_version = ReleaseVersion(9, 9, 9)
        svc.apply_version(new_version, dry_run=True)
        assert read_version(str(Path(temp_pyproject_dir) / "pyproject.toml")) == "1.2.3"

    def test_when_applied_multiple_times_then_correct_version(
        self, temp_pyproject_dir: str
    ) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        svc.apply_version(ReleaseVersion(2, 0, 0))
        svc.apply_version(ReleaseVersion(2, 1, 0))
        assert svc.current_version() == Ok(ReleaseVersion(2, 1, 0))
