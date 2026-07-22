<<<<<<< Updated upstream
from collections.abc import Hashable
from typing import Self
=======
from typing import Hashable, Self
>>>>>>> Stashed changes

from forging_blocks.domain import ValueObject
from forging_releases.domain.errors import InvalidReleaseBranchNameError, InvalidReleaseVersionError
from forging_releases.domain.value_objects.release_version import ReleaseVersion


class ReleaseBranchName(ValueObject[str]):
    __slots__ = ("_value",)

    PREFIX = "release/v"

    def __init__(self, value: str) -> None:
        super().__init__()

        if not value.startswith(self.PREFIX):
            raise InvalidReleaseBranchNameError(value)

        version_part = value[len(self.PREFIX) :]
        parts = version_part.split(".")

        if len(parts) != 3:
            raise InvalidReleaseBranchNameError(value)

        try:
            major, minor, patch = (int(p) for p in parts)
        except ValueError as exc:
            raise InvalidReleaseBranchNameError(value) from exc

        try:
            ReleaseVersion(major, minor, patch)
        except InvalidReleaseVersionError as exc:
            raise InvalidReleaseBranchNameError(value) from exc

        self._value = value

    @classmethod
<<<<<<< Updated upstream
    def create(cls, version: ReleaseVersion) -> Self:
        return cls(f"{cls.PREFIX}{version.value}")

    @classmethod
    def from_str(cls, value: str) -> Result[Self, InvalidReleaseBranchNameError]:
        if not value.startswith(cls.PREFIX):
            return Err(InvalidReleaseBranchNameError(value))

        version_part = value[len(cls.PREFIX) :]
        version_result = ReleaseVersion.from_str(version_part)
        if version_result.is_err:
            return Err(InvalidReleaseBranchNameError(value))

        return Ok(cls(value))

=======
    def from_version(cls, version: ReleaseVersion) -> Self:
        return cls(f"{cls.PREFIX}{version.value}")

>>>>>>> Stashed changes
    @property
    def value(self) -> str:
        return self._value

    @property
    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
