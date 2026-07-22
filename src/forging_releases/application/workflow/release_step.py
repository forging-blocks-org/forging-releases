<<<<<<< Updated upstream
from collections.abc import Callable
=======
>>>>>>> Stashed changes
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ReleaseStep:
    name: str
    undo: Callable[[], None]
