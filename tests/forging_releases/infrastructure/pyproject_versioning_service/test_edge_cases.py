# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import tempfile
from pathlib import Path

import pytest

from forging_releases.infrastructure.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestEdgeCases:
    def test_when_missing_version_key_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            with pytest.raises(ValueError, match="version key not found"):
                svc.current_version()

    def test_when_invalid_version_in_pyproject_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[project]\nversion = "not.a.version"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            with pytest.raises(ValueError, match="Invalid version"):
                svc.current_version()

    def test_when_no_project_section_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[tool]\nkey = "value"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            with pytest.raises(ValueError, match="version key not found"):
                svc.current_version()
