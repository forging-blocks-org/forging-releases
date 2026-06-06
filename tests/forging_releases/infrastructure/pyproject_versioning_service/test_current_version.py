# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import pytest

from forging_releases.domain.value_objects import ReleaseVersion
from forging_releases.infrastructure.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestCurrentVersion:
    def test_when_pyproject_exists_then_reads_version(self, temp_pyproject_dir: str) -> None:
        svc = PyProjectVersioningService(cwd=temp_pyproject_dir)
        version = svc.current_version()
        assert version == ReleaseVersion(1, 2, 3)
        assert version.value == "1.2.3"
