# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_blocks.foundation import Ok

from forging_releases.domain.value_objects import ReleaseVersion
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestRollbackVersion:
    def test_when_rolled_back_then_restores_previous(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        result = svc.current_version()
        assert result.is_ok is True
        original = result.value
        svc.apply_version(ReleaseVersion(5, 0, 0))
        svc.rollback_version(original)
        assert svc.current_version() == Ok(original)
        assert svc.current_version().value.value == "1.2.3"
