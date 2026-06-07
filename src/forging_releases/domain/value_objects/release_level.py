"""Value objects for release levels.

Provides the ``ReleaseLevelEnum`` and ``ReleaseLevel`` types used to
indicate whether a release bumps the major, minor, or patch version.
"""

from collections.abc import Hashable
from enum import StrEnum, auto
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import InvalidReleaseLevelError


class ReleaseLevelEnum(StrEnum):
    """Enumeration of the three supported release bump levels."""

    MAJOR = auto()
    MINOR = auto()
    PATCH = auto()


class ReleaseLevel(ValueObject[ReleaseLevelEnum]):
    """A validated release level indicating which semver segment to bump.

    Wraps a ``ReleaseLevelEnum`` value and ensures the level string is valid
    on construction via ``from_str``.
    """

    __slots__ = ("_level",)

    def __init__(self, level: ReleaseLevelEnum) -> None:
        """Initialize the release level.

        Args:
            level: The release level enum value.
        """
        super().__init__()
        self._level = level
        self._freeze()

    @classmethod
    def from_str(cls, value: str) -> Result[Self, InvalidReleaseLevelError]:
        """Parse a case-insensitive string into a ``ReleaseLevel``.

        Args:
            value: The level string (e.g. ``"major"``, ``"minor"``, ``"patch"``).

        Returns:
            ``Ok(ReleaseLevel)`` if the value matches a known level,
            ``Err(InvalidReleaseLevelError)`` otherwise.
        """
        if value.lower() not in ReleaseLevelEnum:
            return Err(InvalidReleaseLevelError(value))
        return Ok(cls(ReleaseLevelEnum[value.upper()]))

    @property
    def value(self) -> ReleaseLevelEnum:
        """Return the underlying ``ReleaseLevelEnum`` value."""
        return self._level

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._level,)
