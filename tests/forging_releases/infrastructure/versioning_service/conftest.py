# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from forging_releases.infrastructure.versioning_service.pyproject_versioning_service import (
    PyProjectVersioningService,
)

_PYPROJECT_TEMPLATE = """[project]
name = "test-project"
version = "1.2.3"
description = "A test project"
requires-python = ">=3.14"
"""


@pytest.fixture
def temp_pyproject_dir() -> Generator[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        pyproject = Path(tmpdir) / "pyproject.toml"
        pyproject.write_text(_PYPROJECT_TEMPLATE)
        yield tmpdir


def read_version(pyproject_path: str) -> str:
    content = Path(pyproject_path).read_text()
    return PyProjectVersioningService._extract_version(content)
