from pathlib import Path


def test_windows_build_embeds_provided_icon() -> None:
    root = Path(__file__).resolve().parents[2]
    script = (root / "tools" / "build_windows.py").read_text(encoding="utf-8")

    assert (root / "packaging" / "assets" / "dsv_rfid.ico").is_file()
    assert '"--icon"' in script
    assert '"dsv_rfid.ico"' in script
    assert '"--windowed"' in script
