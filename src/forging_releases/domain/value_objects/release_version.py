"""Value objects for semantic release versions.

Provides ReleaseVersion, a validated value object representing a
``<major>.<minor>.<patch>`` semver string with non-negative integer segments.
"""

from collections.abc import Hashable
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import InvalidReleaseVersionError


class ReleaseVersion(ValueObject[str]):
    """A validated semantic version with ``major.minor.patch`` components.

    All version segments must be non-negative integers.
    """

    __slots__ = ("_major", "_minor", "_patch")

    def __init__(self, major: int, minor: int, patch: int) -> None:
        """Initialize a release version from its three integer components.

        Args:
            major: The major version number.
            minor: The minor version number.
            patch: The patch version number.
        """
        super().__init__()

        self._major = major
        self._minor = minor
        self._patch = patch
        self._freeze()

    @classmethod
    def create(cls, major: int, minor: int, patch: int) -> Result[Self, InvalidReleaseVersionError]:
        """Create a ``ReleaseVersion`` after validating that all components are non-negative.

        Args:
            major: The major version number.
            minor: The minor version number.
            patch: The patch version number.

        Returns:
            ``Ok(ReleaseVersion)`` if all components are non-negative,
            ``Err(InvalidReleaseVersionError)`` otherwise.
        """
        if min(major, minor, patch) < 0:
            return Err(InvalidReleaseVersionError(f"{major}.{minor}.{patch}"))
        return Ok(cls(major, minor, patch))

    @classmethod
    def from_str(cls, raw_value: str) -> Result[Self, InvalidReleaseVersionError]:
        """Parse a ``"major.minor.patch"`` string into a ``ReleaseVersion``.

        Args:
            raw_value: The version string to parse.

        Returns:
            ``Ok(ReleaseVersion)`` if the string is well-formed,
            ``Err(InvalidReleaseVersionError)`` otherwise.
        """
        try:
            major, minor, patch = map(int, raw_value.split("."))
            return cls.create(major, minor, patch)
        except Exception:
            return Err(InvalidReleaseVersionError(raw_value))

    @property
    def value(self) -> str:
        """Return the version as a ``"major.minor.patch"`` string."""
        return f"{self._major}.{self._minor}.{self._patch}"

    @property
    def major(self) -> int:
        """Return the major version number."""
        return self._major

    @property
    def minor(self) -> int:
        """Return the minor version number."""
        return self._minor

    @property
    def patch(self) -> int:
        """Return the patch version number."""
        return self._patch

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._major, self._minor, self._patch)
