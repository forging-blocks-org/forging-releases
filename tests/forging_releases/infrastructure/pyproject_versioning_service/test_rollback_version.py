# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_releases.domain.value_objects import ReleaseVersion
from forging_releases.infrastructure.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestRollbackVersion:
    def test_when_rolled_back_then_restores_previous(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        original = svc.current_version()
        svc.apply_version(ReleaseVersion(5, 0, 0))
        svc.rollback_version(original)
        assert svc.current_version() == original
        assert svc.current_version().value == "1.2.3"
