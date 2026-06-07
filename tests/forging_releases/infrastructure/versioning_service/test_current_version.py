# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_releases.domain.value_objects import ReleaseVersion
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestCurrentVersion:
    def test_when_pyproject_exists_then_reads_version(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        result = svc.current_version()
        assert result.is_ok is True
        assert result.value == ReleaseVersion(1, 2, 3)
        assert result.value.value == "1.2.3"
