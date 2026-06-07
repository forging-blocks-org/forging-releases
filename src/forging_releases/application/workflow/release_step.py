from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseStep:
    name: str
    undo: Callable[[], object]
