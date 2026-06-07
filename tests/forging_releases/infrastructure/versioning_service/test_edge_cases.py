# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

import tempfile
from pathlib import Path

import pytest

from forging_releases.application.errors import VersionNotFoundError
from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)


@pytest.mark.integration
class TestEdgeCases:
    def test_when_missing_version_key_then_returns_err(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            result = svc.current_version()
            assert result.is_err is True
            assert isinstance(result.error, VersionNotFoundError)
            assert "version key not found" in result.error.message.value

    def test_when_invalid_version_in_pyproject_then_returns_err(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[project]\nversion = "not.a.version"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            result = svc.current_version()
            assert result.is_err is True
            assert isinstance(result.error, VersionNotFoundError)
            assert "invalid version" in result.error.message.value

    def test_when_no_project_section_then_returns_err(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('[tool]\nkey = "value"\n')
            svc = PyProjectVersioningService(cwd=tmpdir)
            result = svc.current_version()
            assert result.is_err is True
            assert isinstance(result.error, VersionNotFoundError)
            assert "version key not found" in result.error.message.value
