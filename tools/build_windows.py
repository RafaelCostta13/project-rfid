"""Constrói o bundle Windows com recursos QML e plugins Qt pelos hooks oficiais."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Empacotar DSV RFID para Windows.")
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("Execute com Python nativo do Windows; não utilizar WSL.")
    root = Path(__file__).resolve().parents[1]
    output = args.dist_dir.resolve()
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--exclude-module",
        "tkinter",
        "--name",
        "DSV-RFID",
        "--paths",
        str(root / "src"),
        "--collect-data",
        "rfid_reader",
        "--hidden-import",
        "sllurp.llrp",
        "--hidden-import",
        "serial.serialwin32",
        "--hidden-import",
        "pymodbus.client",
        "--distpath",
        str(output),
        "--workpath",
        str(root / "build" / "windows"),
        "--specpath",
        str(root / "build"),
        str(root / "packaging" / "windows_entry.py"),
    ]
    result = subprocess.run(command, cwd=root, check=False)
    if result.returncode:
        return result.returncode
    shutil.copy2(root / ".env.example", output / "DSV-RFID" / ".env.example")
    print(f"Bundle Windows criado em {output / 'DSV-RFID'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
