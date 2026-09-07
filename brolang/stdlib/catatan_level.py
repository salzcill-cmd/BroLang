"""
Modul Catatan Level - Structured Logging untuk BroLang
=======================================================

Sistem logging dengan level, formatter, dan handler.

Contoh:
    impor catatan_level

    catatan_level.info("Server started")
    catatan_level.warning("Disk space low")
    catatan_level.error("Connection failed")
    catatan_level.debug("Variable x = 42")

    # Set level
    catatan_level.set_level("DEBUG")
"""

from types import SimpleNamespace
import logging
import sys
import os
import datetime


# Custom BroLang formatter
class _BroLangFormatter(logging.Formatter):
    """Formatter khusus BroLang."""

    LEVEL_COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelname, '')
        reset = self.RESET if color else ''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        return f"{color}[{timestamp}] {record.levelname}: {record.getMessage()}{reset}"


# Setup default logger
_logger = logging.getLogger('brolang')
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_BroLangFormatter())
_logger.addHandler(_handler)
_logger.setLevel(logging.INFO)


def _set_level(level):
    """Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL."""
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    _logger.setLevel(level_map.get(level.upper(), logging.INFO))


def _debug(msg):
    """Log level DEBUG."""
    _logger.debug(msg)


def _info(msg):
    """Log level INFO."""
    _logger.info(msg)


def _warning(msg):
    """Log level WARNING."""
    _logger.warning(msg)


def _error(msg):
    """Log level ERROR."""
    _logger.error(msg)


def _critical(msg):
    """Log level CRITICAL."""
    _logger.critical(msg)


module = SimpleNamespace(
    set_level=_set_level,
    debug=_debug,
    info=_info,
    warning=_warning,
    error=_error,
    critical=_critical,
)
