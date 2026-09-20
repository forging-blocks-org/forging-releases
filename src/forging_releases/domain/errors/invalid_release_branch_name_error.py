from forging_blocks.foundation import ErrorMessage, ValidationError


class InvalidReleaseBranchNameError(ValidationError):
    def __init__(self, value: str, *, prefix: str = "release/v") -> None:
        super().__init__(
            ErrorMessage(
                f"Invalid release branch name '{value}'. "
                f"Release branches must start with '{prefix}<version>'."
            )
        )
