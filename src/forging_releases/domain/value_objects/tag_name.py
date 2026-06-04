from typing import Hashable, Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result
from forging_releases.domain.errors import (
    InvalidTagNameError,
)
from forging_releases.domain.value_objects.release_version import ReleaseVersion


class TagName(ValueObject[str]):
    __slots__ = ("_value",)

    PREFIX = "v"

    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = value
        self._freeze()

    @classmethod
    def create(cls, value: str) -> Result[Self, InvalidTagNameError]:
        if not value.startswith(cls.PREFIX):
            return Err(InvalidTagNameError(value))

        version_part = value[len(cls.PREFIX) :]
        parts = version_part.split(".")

        if len(parts) != 3:
            return Err(InvalidTagNameError(value))

        try:
            major, minor, patch = (int(p) for p in parts)
        except ValueError:
            return Err(InvalidTagNameError(value))

        version_result = ReleaseVersion.create(major, minor, patch)
        if version_result.is_err:
            return Err(InvalidTagNameError(value))

        return Ok(cls(value))

    @classmethod
    def for_version(cls, version: ReleaseVersion) -> Self:
        return cls(f"{cls.PREFIX}{version.value}")

    @property
    def value(self) -> str:
        return self._value

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
