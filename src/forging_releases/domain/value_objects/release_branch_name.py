from typing import Hashable, Self

from forging_blocks.domain import ValueObject
from forging_releases.domain.errors import InvalidReleaseBranchNameError, InvalidReleaseVersionError
from forging_releases.domain.value_objects.release_version import ReleaseVersion


class ReleaseBranchName(ValueObject[str]):
    __slots__ = ("_value",)

    PREFIX = "release/v"

    def __init__(self, value: str, *, prefix: str = PREFIX) -> None:
        super().__init__()

        if not value.startswith(prefix):
            raise InvalidReleaseBranchNameError(value, prefix=prefix)

        version_part = value[len(prefix) :]
        parts = version_part.split(".")

        if len(parts) != 3:
            raise InvalidReleaseBranchNameError(value, prefix=prefix)

        try:
            major, minor, patch = (int(p) for p in parts)
        except ValueError as exc:
            raise InvalidReleaseBranchNameError(value, prefix=prefix) from exc

        try:
            ReleaseVersion(major, minor, patch)
        except InvalidReleaseVersionError as exc:
            raise InvalidReleaseBranchNameError(value, prefix=prefix) from exc

        self._value = value

    @classmethod
    def from_version(
        cls,
        version: ReleaseVersion,
        *,
        prefix: str | None = None,
    ) -> Self:
        branch_prefix = cls.PREFIX if prefix is None else prefix
        return cls(f"{branch_prefix}{version.value}", prefix=branch_prefix)

    @property
    def value(self) -> str:
        return self._value

    @property
    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
