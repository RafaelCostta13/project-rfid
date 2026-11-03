"""Audita e empacota o bundle Windows para distribuição pelo GitHub Actions."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

REQUIRED_PATHS = ("DSV-RFID.exe", "_internal", ".env.example")
FORBIDDEN_FILENAMES = frozenset({".env", "station.env"})
FORBIDDEN_SUFFIXES = frozenset({".key", ".pem", ".sqlite", ".sqlite3", ".db"})
FORBIDDEN_DIRECTORIES = frozenset({".git", ".github", ".venv", "logs", "__pycache__"})
SENSITIVE_ENV_KEYWORDS = ("TOKEN", "PASSWORD", "SECRET", "PRIVATE_KEY")


class DistributionAuditError(RuntimeError):
    """O bundle contém algo ausente, proibido ou não distribuível."""


def _validate_env_example(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if any(keyword in name.upper() for keyword in SENSITIVE_ENV_KEYWORDS) and value.strip():
            raise DistributionAuditError(f".env.example contém valor sensível: {name}")


def _validate_bundle(bundle: Path) -> list[Path]:
    if bundle.name != "DSV-RFID" or not bundle.is_dir():
        raise DistributionAuditError("o bundle deve ser o diretório DSV-RFID")
    for required in REQUIRED_PATHS:
        path = bundle / required
        if not path.exists():
            raise DistributionAuditError(f"recurso obrigatório ausente: {required}")
    _validate_env_example(bundle / ".env.example")
    files: list[Path] = []
    for path in bundle.rglob("*"):
        relative = path.relative_to(bundle)
        parts = {part.casefold() for part in relative.parts}
        if path.is_symlink():
            raise DistributionAuditError(f"link simbólico não permitido: {relative}")
        if parts & FORBIDDEN_DIRECTORIES:
            raise DistributionAuditError(f"diretório proibido no bundle: {relative}")
        if not path.is_file():
            continue
        name = path.name.casefold()
        if name in FORBIDDEN_FILENAMES or path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            raise DistributionAuditError(f"arquivo sensível ou operacional proibido: {relative}")
        files.append(path)
    if not files:
        raise DistributionAuditError("o bundle não contém arquivos para distribuição")
    return sorted(files)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_distribution(
    bundle: Path,
    output_directory: Path,
    commit: str,
    branch: str,
    python_version: str,
    pyinstaller_version: str,
) -> tuple[Path, Path, dict[str, str | int]]:
    """Cria ZIP e checksum após uma auditoria restritiva do bundle."""

    files = _validate_bundle(bundle)
    short_commit = commit[:7]
    if len(short_commit) != 7 or not all(
        character in "0123456789abcdef" for character in short_commit
    ):
        raise DistributionAuditError(
            "commit deve iniciar com ao menos sete caracteres hexadecimais"
        )
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"DSV-RFID-Windows-{short_commit}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for path in files:
            target.write(path, Path(bundle.name) / path.relative_to(bundle))
    checksum = _sha256(archive)
    checksum_path = archive.with_suffix(".sha256")
    checksum_path.write_text(f"{archive.name}\nSHA256: {checksum}\n", encoding="utf-8")
    report: dict[str, str | int] = {
        "archive": archive.name,
        "branch": branch,
        "commit": commit,
        "files": len(files),
        "pyinstaller": pyinstaller_version,
        "python": python_version,
        "sha256": checksum,
        "size_bytes": archive.stat().st_size,
    }
    return archive, checksum_path, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auditar e zipar o bundle DSV RFID para Windows.")
    parser.add_argument("--bundle", type=Path, default=Path("dist/DSV-RFID"))
    parser.add_argument("--output-dir", type=Path, default=Path("build/release"))
    parser.add_argument("--commit", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--python-version", default=sys.version.split()[0])
    parser.add_argument("--pyinstaller-version", required=True)
    args = parser.parse_args(argv)
    try:
        _, _, report = package_distribution(
            args.bundle.resolve(),
            args.output_dir.resolve(),
            args.commit.lower(),
            args.branch,
            args.python_version,
            args.pyinstaller_version,
        )
    except (DistributionAuditError, OSError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
