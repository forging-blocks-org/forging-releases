"""Error returned when a release branch already exists with the same changes."""


class ReleaseBranchExistsError(Exception):
    """Represents an attempt to create a release branch that already exists with no new changes."""

    def __init__(self, branch_name: str) -> None:
        self.branch_name = branch_name
        super().__init__(f"Release branch '{branch_name}' already exists with the same changes")
