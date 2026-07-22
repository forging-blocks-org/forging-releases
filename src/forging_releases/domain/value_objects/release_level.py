<<<<<<< Updated upstream
from collections.abc import Hashable
=======
from __future__ import annotations

>>>>>>> Stashed changes
from enum import StrEnum, auto
from typing import Hashable

from forging_blocks.domain import ValueObject
from forging_releases.domain.errors import InvalidReleaseLevelError


class ReleaseLevelEnum(StrEnum):
    MAJOR = auto()
    MINOR = auto()
    PATCH = auto()


class ReleaseLevel(ValueObject[ReleaseLevelEnum]):
    __slots__ = ("_level",)

    def __init__(self, level: ReleaseLevelEnum) -> None:
        super().__init__()
        self._level = level

    @classmethod
<<<<<<< Updated upstream
    def from_str(cls, value: str) -> Result[Self, InvalidReleaseLevelError]:
=======
    def from_str(cls, value: str) -> ReleaseLevel:
>>>>>>> Stashed changes
        if value.lower() not in ReleaseLevelEnum:
            raise InvalidReleaseLevelError(value)
        return cls(ReleaseLevelEnum[value.upper()])

    @property
    def value(self) -> ReleaseLevelEnum:
        return self._level

    @property
    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._level,)
