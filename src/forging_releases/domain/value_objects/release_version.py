from collections.abc import Hashable
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import InvalidReleaseVersionError


class ReleaseVersion(ValueObject[str]):
    __slots__ = ("_major", "_minor", "_patch")

    def __init__(self, major: int, minor: int, patch: int) -> None:
        super().__init__()

        self._major = major
        self._minor = minor
        self._patch = patch
        self._freeze()

    @classmethod
    def create(
        cls, major: int, minor: int, patch: int
    ) -> Result[Self, InvalidReleaseVersionError]:
        if min(major, minor, patch) < 0:
            return Err(InvalidReleaseVersionError(f"{major}.{minor}.{patch}"))
        return Ok(cls(major, minor, patch))

    @classmethod
    def from_str(cls, raw_value: str) -> Result[Self, InvalidReleaseVersionError]:
        try:
            major, minor, patch = map(int, raw_value.split("."))
            return cls.create(major, minor, patch)
        except Exception:
            return Err(InvalidReleaseVersionError(raw_value))

    @property
    def value(self) -> str:
        return f"{self._major}.{self._minor}.{self._patch}"

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return self._patch

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._major, self._minor, self._patch)
