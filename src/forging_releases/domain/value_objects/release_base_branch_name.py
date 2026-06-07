"""Value objects for release base branch names.

Provides ReleaseBaseBranchName, a validated value object representing the
target base branch for a release pull request.
"""

from collections.abc import Hashable
from typing import Self

from forging_blocks.domain import ValueObject
from forging_blocks.foundation import Err, Ok, Result

from forging_releases.domain.errors import InvalidReleaseBranchNameError


class ReleaseBaseBranchName(ValueObject[str]):
    """A validated release base branch name following the ``release/v<version>`` convention.

    Attributes:
        PREFIX: The constant prefix ``release/v`` used for all base branches.
    """

    __slots__ = ("_value",)

    PREFIX = "release/v"

    def __init__(self, value: str) -> None:
        """Initialize the release base branch name.

        Args:
            value: The raw base branch name string.
        """
        super().__init__()

        self._value = value
        self._freeze()

    @classmethod
    def from_string(cls, value: str) -> Result[Self, InvalidReleaseBranchNameError]:
        """Parse a string into a validated ``ReleaseBaseBranchName``.

        Args:
            value: The raw branch name string.

        Returns:
            ``Ok(ReleaseBaseBranchName)`` if the value starts with the required prefix,
            ``Err(InvalidReleaseBranchNameError)`` otherwise.
        """
        match value:
            case str(value) if value.startswith(cls.PREFIX):
                return Ok(cls(value))
            case _:
                return Err(InvalidReleaseBranchNameError(value))

    @property
    def value(self) -> str:
        """Return the raw base branch name string."""
        return self._value

    def _equality_components(self) -> tuple[Hashable, ...]:
        return (self._value,)
