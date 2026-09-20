from collections.abc import Sequence
from typing import Any

import pytest

from forging_releases.presentation import __main__ as main_module


@pytest.mark.unit
class TestMain:
    def test_main_runs_presenter_for_explicit_arguments(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen: list[Sequence[str] | None] = []

        class RecordingPresenter:
            def __init__(self, _parser: Any, _factory: Any) -> None:
                pass

            async def present(self, argv: Sequence[str] | None = None) -> None:
                seen.append(argv)

        monkeypatch.setattr(main_module, "ReleaseCliPresenter", RecordingPresenter)

        main_module.main(["minor", "--execute"])

        assert seen == [["minor", "--execute"]]

    def test_main_passes_none_to_presenter(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen: list[Sequence[str] | None] = []

        class RecordingPresenter:
            def __init__(self, _parser: Any, _factory: Any) -> None:
                pass

            async def present(self, argv: Sequence[str] | None = None) -> None:
                seen.append(argv)

        monkeypatch.setattr(main_module, "ReleaseCliPresenter", RecordingPresenter)

        main_module.main(None)

        assert seen == [None]
