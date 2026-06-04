from forging_releases import main


def test_dummy() -> None:
    assert True is True


def test_main_when_called_then_prints(capsys: object) -> None:
    from typing import cast
    from pytest import CaptureFixture

    main()
    captured = cast(CaptureFixture[str], capsys).readouterr()
    assert "Hello from forging-releases!" in captured.out
