"""Operação Qt oficial, com modos explícitos de prévia e configuração local."""

import argparse
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from rfid_reader.config import ConfigurationError, load_config
from rfid_reader.ui.qt.mock_data import PrototypeScenario, PrototypeTheme


def main(
    argv: Sequence[str] | None = None,
    environment: Mapping[str, str] | None = None,
    configuration_path: Path | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        prog="rfid-reader",
        description="DSV RFID: operação Qt. Use --preview ou --configure para abrir sem hardware.",
    )
    parser.add_argument("--theme", choices=list(PrototypeTheme), default=PrototypeTheme.CORPORATE)
    parser.add_argument(
        "--scenario", choices=list(PrototypeScenario), help="Cenário simulado do modo --preview."
    )
    parser.add_argument("--windowed", action="store_true", help="Não abrir maximizado.")
    parser.add_argument(
        "--size", type=int, nargs=2, default=(1366, 768), metavar=("LARGURA", "ALTURA")
    )
    parser.add_argument(
        "--screenshot", type=Path, help="Salvar uma captura PNG e encerrar a prévia."
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--preview", action="store_true", help="Abrir prévia simulada, sem hardware."
    )
    modes.add_argument(
        "--configure", action="store_true", help="Ler/salvar configurações locais, sem hardware."
    )
    modes.add_argument(
        "--operate", action="store_true", help="Operar pela interface Qt (modo padrão)."
    )
    parser.add_argument("--env-file", type=Path, help="Arquivo .env da operação ou configuração.")
    parser.add_argument("--page", choices=("start", "settings"), default="start")
    args = parser.parse_args(argv)
    if args.size[0] < 850 or args.size[1] < 480:
        parser.error("O tamanho mínimo é 850 × 480 pixels lógicos.")
    if args.screenshot is not None and args.screenshot.suffix.lower() != ".png":
        parser.error("A captura deve utilizar a extensão .png.")
    operational = not (args.preview or args.configure)
    if args.preview and (args.env_file is not None or args.page != "start"):
        parser.error("--env-file e --page settings exigem operação ou --configure.")
    if not args.preview and args.scenario is not None:
        parser.error("Cenários simulados exigem --preview.")
    if operational and args.screenshot is not None:
        parser.error("Capturas automáticas são exclusivas dos modos sem hardware.")
    try:
        from rfid_reader.ui.qt.application import PrototypeError
    except ModuleNotFoundError as error:
        if error.name is None or not error.name.startswith("PySide6"):
            raise
        print('PySide6 não instalado. Execute: python -m pip install -e "."', file=sys.stderr)
        return 1
    try:
        if not args.preview:
            path = args.env_file or configuration_path
            if path is None:
                discovered = find_dotenv(usecwd=True) if environment is None else ""
                path = Path(discovered) if discovered else Path.cwd() / ".env"
            if environment is None:
                load_dotenv(dotenv_path=path)
            settings = load_config(environment)
            if operational:
                from rfid_reader.ui.qt.application import run_operational

                return run_operational(
                    settings,
                    path,
                    PrototypeTheme(args.theme),
                    windowed=args.windowed,
                    size=(args.size[0], args.size[1]),
                    initial_page=args.page,
                )
            from rfid_reader.ui.qt.application import run_configuration

            return run_configuration(
                settings,
                path,
                PrototypeTheme(args.theme),
                windowed=args.windowed,
                size=(args.size[0], args.size[1]),
                screenshot=args.screenshot,
                initial_page=args.page,
            )
        from rfid_reader.ui.qt.application import run_prototype

        return run_prototype(
            PrototypeTheme(args.theme),
            PrototypeScenario(args.scenario or PrototypeScenario.READY),
            windowed=args.windowed,
            size=(args.size[0], args.size[1]),
            screenshot=args.screenshot,
        )
    except ConfigurationError as error:
        print(f"Erro de configuração: {error}", file=sys.stderr)
        return 2
    except (PrototypeError, RuntimeError, OSError) as error:
        print(f"Erro na interface Qt: {error}", file=sys.stderr)
        return 1


def run() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    run()
