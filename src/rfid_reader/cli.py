"""Interface de linha de comando da aplicação."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from rfid_reader.config import ConfigurationError, Settings, load_config


def _print_summary(settings: Settings) -> None:
    antennas = ", ".join(map(str, settings.antennas))
    print("Configuração válida")
    print(f"Reader: {settings.reader_name}")
    print(f"Host: {settings.reader_host}:{settings.reader_port}")
    print(f"Antenas: {antennas}")
    print(f"Log level: {settings.log_level}")


def _check_config(
    argv: Sequence[str],
    environment: Mapping[str, str] | None,
    configuration_path: Path | None,
) -> int:
    parser = argparse.ArgumentParser(prog="rfid-reader check-config")
    parser.add_argument(
        "--env-file", type=Path, help="Arquivo .env a validar, sem conectar serviços."
    )
    arguments = parser.parse_args(argv)
    path = arguments.env_file or configuration_path
    if path is None:
        if environment is None:
            discovered = find_dotenv(usecwd=True)
            path = Path(discovered) if discovered else Path.cwd() / ".env"
        else:
            path = Path.cwd() / ".env"
    if environment is None:
        load_dotenv(dotenv_path=path)
    try:
        settings = load_config(environment)
    except ConfigurationError as error:
        print(f"Erro de configuração: {error}", file=sys.stderr)
        return 2

    _print_summary(settings)
    return 0


def main(
    argv: Sequence[str] | None = None,
    environment: Mapping[str, str] | None = None,
    configuration_path: Path | None = None,
) -> int:
    """Abre a operação Qt por padrão; check-config permanece sem UI ou rede."""

    options = list(sys.argv[1:] if argv is None else argv)
    if options and options[0] == "check-config":
        return _check_config(options[1:], environment, configuration_path)
    if options and options[0] == "show":
        options = options[1:]
    from rfid_reader.cli_qt import main as qt_main

    return qt_main(options, environment, configuration_path)


def run() -> None:
    """Ponto de entrada do script instalado."""

    raise SystemExit(main())


if __name__ == "__main__":
    run()
