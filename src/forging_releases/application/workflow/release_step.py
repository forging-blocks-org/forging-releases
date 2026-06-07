"""Defines a single reversible step within the release transaction workflow."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseStep:
    """A reversible operation registered with the release transaction.

    Attributes:
        name: Human-readable label identifying this step.
        undo: Callable that reverses the step's effect during rollback.
    """

    name: str
    undo: Callable[[], object]
