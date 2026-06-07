"""Value objects for Git tag names.

Provides TagName, a validated value object representing a Git tag following
the ``v<semver>`` naming convention.
"""

from collections.abc import Hashable
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import (
    InvalidTagNameError,
)
from forging_releases.domain.value_objects.release_version import ReleaseVersion


class TagName(ValueObject[str]):
    """A validated Git tag name following the ``v<version>`` convention.

    Attributes:
        PREFIX: The constant prefix ``v`` used for all release tags.
    """

    __slots__ = ("_value",)

    PREFIX = "v"

    def __init__(self, value: str) -> None:
        """Initialize the tag name.

        Args:
            value: The raw tag name string.
        """
        super().__init__()

        self._value = value
        self._freeze()

    @classmethod
    def create(cls, version: ReleaseVersion) -> Self:
        """Create a tag name from a ``ReleaseVersion``.

        Args:
            version: The release version to derive the tag name from.

        Returns:
            A new ``TagName`` instance.
        """
        return cls(f"{cls.PREFIX}{version.value}")

    @classmethod
    def from_str(cls, value: str) -> Result[Self, InvalidTagNameError]:
        """Parse a tag name string into a ``TagName``.

        Args:
            value: The raw tag name string to validate.

        Returns:
            ``Ok(TagName)`` if the value starts with the ``v`` prefix and
            contains a valid version, ``Err(InvalidTagNameError)`` otherwise.
        """
        if not value.startswith(cls.PREFIX):
            return Err(InvalidTagNameError(value))

        version_part = value[len(cls.PREFIX) :]
        version_result = ReleaseVersion.from_str(version_part)
        if version_result.is_err:
            return Err(InvalidTagNameError(value))

        return Ok(cls(value))

    @property
    def value(self) -> str:
        """Return the raw tag name string."""
        return self._value

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
