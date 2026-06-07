"""Value objects for release branch names.

Provides ReleaseBranchName, a validated value object that represents a Git
release branch following the ``release/v<semver>`` naming convention.
"""

from collections.abc import Hashable
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import (
    InvalidReleaseBranchNameError,
)
from forging_releases.domain.value_objects.release_version import ReleaseVersion


class ReleaseBranchName(ValueObject[str]):
    """A validated release branch name following the ``release/v<version>`` convention.

    Attributes:
        PREFIX: The constant prefix ``release/v`` used for all release branches.
    """

    __slots__ = ("_value",)

    PREFIX = "release/v"

    def __init__(self, value: str) -> None:
        """Initialize the release branch name.

        Args:
            value: The raw branch name string.
        """
        super().__init__()

        self._value = value
        self._freeze()

    @classmethod
    def create(cls, version: ReleaseVersion) -> Self:
        """Create a release branch name from a ``ReleaseVersion``.

        Args:
            version: The release version to derive the branch name from.

        Returns:
            A new ``ReleaseBranchName`` instance.
        """
        return cls(f"{cls.PREFIX}{version.value}")

    @classmethod
    def from_str(cls, value: str) -> Result[Self, InvalidReleaseBranchNameError]:
        """Parse a branch name string into a ``ReleaseBranchName``.

        Args:
            value: The raw branch name string to validate.

        Returns:
            ``Ok(ReleaseBranchName)`` if the value is valid,
            ``Err(InvalidReleaseBranchNameError)`` otherwise.
        """
        if not value.startswith(cls.PREFIX):
            return Err(InvalidReleaseBranchNameError(value))

        version_part = value[len(cls.PREFIX) :]
        version_result = ReleaseVersion.from_str(version_part)
        if version_result.is_err:
            return Err(InvalidReleaseBranchNameError(value))

        return Ok(cls(value))

    @property
    def value(self) -> str:
        """Return the raw branch name string."""
        return self._value

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
