"""Command for opening a release pull request.

Provides ``OpenPullRequestCommand``, the command message used to trigger the
creation of a release pull request with a given version, branch, and dry-run
flag.
"""

from forging_blocks.foundation.messages.command import Command

type PayloadType = dict[str, str | bool]


class OpenPullRequestCommand(Command[PayloadType]):
    """Command to open a release pull request.

    Captures the version, target branch, and dry-run flag needed to create a
    release pull request through the application layer.
    """

    def __init__(self, *, version: str, branch: str, dry_run: bool) -> None:
        """Initialize the command.

        Args:
            version: The release version string.
            branch: The target branch name.
            dry_run: If ``True``, simulate the operation without side effects.
        """
        self._version = version
        self._branch = branch
        self._dry_run = dry_run
        self._value: PayloadType = {
            "version": self._version,
            "branch": self._branch,
            "dry_run": self._dry_run,
        }

        super().__init__()

    @property
    def value(self) -> PayloadType:
        """Return the command payload as a dictionary."""
        return self._value

    @property
    def version(self) -> str:
        """Return the release version string."""
        return self._version

    @property
    def branch(self) -> str:
        """Return the target branch name."""
        return self._branch

    @property
    def dry_run(self) -> bool:
        """Return whether this is a dry-run operation."""
        return self._dry_run

    @property
    def _payload(self) -> PayloadType:
        return self._value
