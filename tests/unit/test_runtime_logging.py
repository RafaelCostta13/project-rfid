"""Testes do logging persistente independente de UI e hardware."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rfid_reader.logging_config import (
    LOG_BACKUP_COUNT,
    LOG_FILENAME,
    LOG_MAX_BYTES,
    PERSISTENT_LOG_HANDLER_NAME,
    configure_logging,
)


def _persistent_handlers() -> list[logging.Handler]:
    return [
        handler
        for handler in logging.getLogger().handlers
        if handler.name == PERSISTENT_LOG_HANDLER_NAME
    ]


def _remove_persistent_handlers() -> None:
    root_logger = logging.getLogger()
    for handler in _persistent_handlers():
        root_logger.removeHandler(handler)
        handler.close()


def test_configure_logging_creates_one_utf8_rotating_log(tmp_path: Path) -> None:
    _remove_persistent_handlers()
    try:
        log_path = configure_logging("INFO", tmp_path / "logs")
        assert log_path == tmp_path / "logs" / LOG_FILENAME
        handlers = _persistent_handlers()
        assert len(handlers) == 1
        handler = handlers[0]
        assert isinstance(handler, RotatingFileHandler)
        assert handler.maxBytes == LOG_MAX_BYTES
        assert handler.backupCount == LOG_BACKUP_COUNT
        assert handler.encoding == "utf-8"
        logging.getLogger("rfid_reader.test").info("persistent-log-test")
        handler.flush()
        assert "persistent-log-test" in log_path.read_text(encoding="utf-8")
        assert configure_logging("DEBUG", tmp_path / "logs") == log_path
        assert len(_persistent_handlers()) == 1
    finally:
        _remove_persistent_handlers()


def test_configure_logging_keeps_application_running_when_directory_is_unavailable(
    tmp_path: Path,
) -> None:
    _remove_persistent_handlers()
    unavailable = tmp_path / "not-a-directory"
    unavailable.write_text("blocked", encoding="utf-8")
    try:
        assert configure_logging("INFO", unavailable) is None
        assert not _persistent_handlers()
    finally:
        _remove_persistent_handlers()
