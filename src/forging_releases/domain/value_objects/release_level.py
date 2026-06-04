from enum import StrEnum, auto
from typing import Hashable, Self

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
        self._freeze()

    @classmethod
    def from_str(cls, value: str) -> Self:
        if value.lower() not in ReleaseLevelEnum:
            raise InvalidReleaseLevelError(value)
        return cls(ReleaseLevelEnum[value.upper()])

    @property
    def value(self) -> ReleaseLevelEnum:
        return self._level

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._level,)
