"""Fake CommandRunner implementation for infrastructure tests.

Configurable responses replace real subprocess calls. Tests verify
behaviour through recorded calls and configured outputs, not
through mock interaction assertions.
"""

from collections.abc import Sequence

from forging_releases.application.ports.outbound import CommandRunner


class FakeCommandRunner(CommandRunner):
    """State-based CommandRunner fake.

    ``responses`` is an ordered list — each ``run()`` call pops the
    first entry. Entries may be a ``str`` (success) or an
    ``Exception`` to raise.
    """

    def __init__(self, *configured_outputs: str | Exception) -> None:
        self.configured_outputs: list[str | Exception] = list(configured_outputs)
        self.calls: list[tuple[list[str], bool]] = []

    def run(
        self,
        command: Sequence[str],
        *,
        check: bool = True,
    ) -> str:
        self.calls.append((list(command), check))

        if not self.configured_outputs:
            return ""

        output = self.configured_outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return output
