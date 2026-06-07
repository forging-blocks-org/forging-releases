# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_releases.domain.value_objects import ReleaseLevel, ReleaseLevelEnum, ReleaseVersion
from forging_releases.infrastructure.versioning_service.versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestComputeNextVersion:
    def test_when_major_level_then_bumps_major(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        level = ReleaseLevel(ReleaseLevelEnum.MAJOR)
        next_ver = svc.compute_next_version(level)
        assert next_ver == ReleaseVersion(2, 0, 0)

    def test_when_minor_level_then_bumps_minor(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        level = ReleaseLevel(ReleaseLevelEnum.MINOR)
        next_ver = svc.compute_next_version(level)
        assert next_ver == ReleaseVersion(1, 3, 0)

    def test_when_patch_level_then_bumps_patch(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        level = ReleaseLevel(ReleaseLevelEnum.PATCH)
        next_ver = svc.compute_next_version(level)
        assert next_ver == ReleaseVersion(1, 2, 4)
