from collections.abc import Hashable
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import InvalidReleaseBranchNameError


class ReleaseBaseBranchName(ValueObject[str]):
    __slots__ = ("_value",)

    PREFIX = "release/v"

    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = value
        self._freeze()

    @classmethod
    def from_string(cls, value: str) -> Result[Self, InvalidReleaseBranchNameError]:
        match value:
            case str(value) if value.startswith(cls.PREFIX):
                return Ok(cls(value))
            case _:
                return Err(InvalidReleaseBranchNameError(value))

    @property
    def value(self) -> str:
        return self._value

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
