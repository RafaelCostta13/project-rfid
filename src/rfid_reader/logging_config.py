"""Configuração de logs independente da composição operacional."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILENAME = "rfid-system.log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5
PERSISTENT_LOG_HANDLER_NAME = "rfid-persistent-log"

LOGGER = logging.getLogger(__name__)


def _default_log_directory() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return base / "DSV-RFID" / "logs"


def configure_logging(level: str, log_directory: Path | None = None) -> Path | None:
    """Configura logs no console e em arquivo rotativo quando possível."""

    logging.basicConfig(level=level, format=LOG_FORMAT)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    directory = log_directory or _default_log_directory()
    log_path = directory / LOG_FILENAME
    for handler in root_logger.handlers:
        if handler.name == PERSISTENT_LOG_HANDLER_NAME:
            handler.setLevel(level)
            return log_path
    try:
        directory.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            log_path,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError:
        LOGGER.warning("persistent_logging_unavailable path=%s", log_path, exc_info=True)
        return None
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.name = PERSISTENT_LOG_HANDLER_NAME
    root_logger.addHandler(handler)
    handler.handle(
        LOGGER.makeRecord(
            LOGGER.name,
            logging.INFO,
            __file__,
            0,
            "persistent_logging_configured log_file=%s",
            (str(log_path),),
            None,
        )
    )
    return log_path
