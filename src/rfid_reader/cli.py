"""Interface de linha de comando da aplicação."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence

from dotenv import load_dotenv

from rfid_reader.application import ApplicationError, run_application
from rfid_reader.config import ConfigurationError, Settings, load_config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rfid-reader")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("check-config", help="valida a configuração local")
    subcommands.add_parser("show", help="abre a tela principal")
    return parser


def _print_summary(settings: Settings) -> None:
    antennas = ", ".join(map(str, settings.antennas))
    print("Configuração válida")
    print(f"Reader: {settings.reader_name}")
    print(f"Host: {settings.reader_host}:{settings.reader_port}")
    print(f"Antenas: {antennas}")
    print(f"Log level: {settings.log_level}")


def main(
    argv: Sequence[str] | None = None,
    environment: Mapping[str, str] | None = None,
) -> int:
    """Executa a CLI e retorna um código de saída."""

    arguments = _parser().parse_args(argv)
    if environment is None:
        load_dotenv()
    try:
        settings = load_config(environment)
    except ConfigurationError as error:
        print(f"Erro de configuração: {error}", file=sys.stderr)
        return 2

    if arguments.command == "check-config":
        _print_summary(settings)
        return 0
    if arguments.command == "show":
        try:
            run_application(settings)
        except ApplicationError as error:
            print(f"Erro ao iniciar aplicação: {error}", file=sys.stderr)
            return 1
        return 0
    return 1


def run() -> None:
    """Ponto de entrada do script instalado."""

    raise SystemExit(main())


if __name__ == "__main__":
    run()
