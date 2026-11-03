"""Testes da auditoria de distribuição Windows sem PyInstaller ou hardware."""

from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "package_windows.py"
SPEC = importlib.util.spec_from_file_location("package_windows", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


def bundle(tmp_path: Path) -> Path:
    directory = tmp_path / "DSV-RFID"
    (directory / "_internal").mkdir(parents=True)
    (directory / "DSV-RFID.exe").write_bytes(b"executable")
    (directory / ".env.example").write_text("RFID_READER_HOST=reader.invalid\n", encoding="utf-8")
    (directory / "_internal" / "python312.dll").write_bytes(b"library")
    return directory


def test_package_distribution_contains_complete_bundle_and_checksum(tmp_path: Path) -> None:
    source = bundle(tmp_path)
    archive, checksum, report = PACKAGE.package_distribution(
        source, tmp_path / "release", "a1b2c3d4e5f6", "main", "3.12.10", "6.22.3"
    )
    assert archive.name == "DSV-RFID-Windows-a1b2c3d.zip"
    assert checksum.read_text(encoding="utf-8").startswith(f"{archive.name}\nSHA256: ")
    assert report["branch"] == "main"
    with zipfile.ZipFile(archive) as packaged:
        assert sorted(packaged.namelist()) == [
            "DSV-RFID/.env.example",
            "DSV-RFID/DSV-RFID.exe",
            "DSV-RFID/_internal/python312.dll",
        ]


@pytest.mark.parametrize(
    "relative", [".env", "station.env", "_internal/private.pem", "logs/app.log"]
)
def test_package_distribution_rejects_sensitive_or_operational_files(
    tmp_path: Path, relative: str
) -> None:
    source = bundle(tmp_path)
    prohibited = source / relative
    prohibited.parent.mkdir(parents=True, exist_ok=True)
    prohibited.write_text("not for distribution", encoding="utf-8")
    with pytest.raises(PACKAGE.DistributionAuditError):
        PACKAGE.package_distribution(
            source, tmp_path / "release", "a1b2c3d4e5f6", "main", "3.12.10", "6.22.3"
        )


def test_package_distribution_rejects_populated_sensitive_example_value(tmp_path: Path) -> None:
    source = bundle(tmp_path)
    (source / ".env.example").write_text("API_TOKEN=not-for-distribution\n", encoding="utf-8")
    with pytest.raises(PACKAGE.DistributionAuditError, match="API_TOKEN"):
        PACKAGE.package_distribution(
            source, tmp_path / "release", "a1b2c3d4e5f6", "main", "3.12.10", "6.22.3"
        )
