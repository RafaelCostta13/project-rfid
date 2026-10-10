"""Smoke test do executável nativo em cwd separado, sem hardware ou ambiente Python."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Verificar o bundle Windows sem equipamentos.")
    parser.add_argument("--bundle", type=Path, default=Path("dist/DSV-RFID"))
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    executable = bundle / "DSV-RFID.exe"
    root = Path(__file__).resolve().parents[1]
    output = root / "build" / "rf018-distribution-smoke"
    output.mkdir(parents=True, exist_ok=True)
    settings = output / "simulated.env"
    content = "RFID_READER_HOST=reader.invalid\nRFID_READER_NAME=Simulado\nRFID_BACKEND_BASE_URL=https://backend.invalid\n"
    settings.write_text(content, encoding="utf-8")
    environment = dict(os.environ)
    for key in tuple(environment):
        if key.startswith(("RFID_", "WAVESHARE_", "SHAREPOINT_", "DATABASE_")):
            environment.pop(key)
    for key in (
        "PYTHONPATH",
        "PYTHONHOME",
        "VIRTUAL_ENV",
        "QT_PLUGIN_PATH",
        "QML_IMPORT_PATH",
        "QML2_IMPORT_PATH",
    ):
        environment.pop(key, None)
    environment["PATH"] = str(Path(environment.get("SystemRoot", "C:/Windows")) / "System32")
    environment["QT_QPA_PLATFORM"] = "offscreen"
    environment["QT_QUICK_BACKEND"] = "software"
    environment["QT_QPA_FONTDIR"] = str(Path(environment.get("SystemRoot", "C:/Windows")) / "Fonts")
    captures = (
        ("start.png", ["--preview"]),
        ("settings.png", ["--configure", "--page", "settings", "--env-file", str(settings)]),
    )
    for name, mode in captures:
        capture = output / name
        result = subprocess.run(
            [str(executable), *mode, "--windowed", "--screenshot", str(capture)],
            cwd=output,
            env=environment,
            capture_output=True,
            text=True,
            timeout=45,
            creationflags=subprocess.CREATE_NO_WINDOW,
            check=False,
        )
        if result.returncode or result.stderr.strip():
            raise RuntimeError(f"Falha no smoke test {name}: {result.stderr}")
        if capture.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Captura inválida: {name}")
    if settings.read_text(encoding="utf-8") != content:
        raise RuntimeError("O smoke test alterou a configuração fictícia.")
    assets = bundle / "_internal" / "rfid_reader" / "ui" / "qml"
    required = (
        assets / "Main.qml",
        assets / "pages" / "DiagnosticPage.qml",
        assets / "assets" / "branding" / "dsv_logo.svg",
        bundle / "_internal" / "python312.dll",
        bundle / "_internal" / "PySide6" / "plugins" / "platforms" / "qwindows.dll",
    )
    for path in required:
        if not path.is_file():
            raise RuntimeError(f"Recurso ausente no bundle: {path.relative_to(bundle)}")
    if list(bundle.rglob("_tkinter*")) or list(bundle.rglob("_tcl_data")):
        raise RuntimeError("O bundle ainda contém o toolkit Tkinter removido.")
    checked = subprocess.run(
        [str(executable), "check-config", "--env-file", str(settings)],
        cwd=output,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=False,
    )
    if checked.returncode or checked.stderr.strip() or "Simulado" not in checked.stdout:
        raise RuntimeError("A CLI oficial do bundle não validou a configuração fictícia.")
    if (assets / "assets" / "branding" / "dsv_logo.svg").read_bytes() != (
        root / "assets" / "branding" / "dsv_logo.svg"
    ).read_bytes():
        raise RuntimeError("O branding distribuído difere do aprovado.")
    print(f"Bundle validado sem Python no PATH ou hardware. Capturas em {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
