"""Logging configuration for Bad Weather Mount Tester."""

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_and_create_log_dir() -> Path:
    """Return the platform-specific log directory, creating it if needed.

    Falls back to the current working directory if the platform directory
    cannot be created.
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Local"))
        log_dir = base / "BWMT" / "logs"
    elif sys.platform == "darwin":
        log_dir = Path.home() / "Library" / "Logs" / "BWMT"
    else:
        # Linux / Raspberry Pi: XDG_DATA_HOME or fallback
        xdg = os.environ.get("XDG_DATA_HOME", "")
        if xdg:
            log_dir = Path(xdg) / "bwmt" / "logs"
        else:
            log_dir = Path.home() / ".local" / "share" / "bwmt" / "logs"

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        log_dir = Path(".")

    return log_dir


def _rotate_logs(log_dir: Path) -> None:
    """Remove oldest log files, keeping at most 19 (leaving room for the new one)."""
    existing = sorted(log_dir.glob("bwmt_*.log"), key=lambda p: p.stat().st_mtime)
    while len(existing) >= 20:
        existing.pop(0).unlink(missing_ok=True)


def setup_logging(config_path: Optional[Path] = None) -> Path:
    """Set up logging and return the path of the log file created.

    Config precedence:
    1. ``config_path`` (CLI ``--log-config``)
    2. ``logging.ini`` in the user data dir (sibling of log dir)
    3. Bundled ``logging_errors.ini`` (errors-only default)
    """
    log_dir = get_and_create_log_dir()

    _rotate_logs(log_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"bwmt_{timestamp}.log"

    # Determine which config file to use
    bundled_errors_ini = Path(__file__).parent / "logging_verbose.ini"
    user_logging_ini = log_dir.parent / "logging.ini"

    if config_path is not None and Path(config_path).exists():
        ini_path = Path(config_path)
    elif user_logging_ini.exists():
        ini_path = user_logging_ini
    else:
        ini_path = bundled_errors_ini

    # Convert log file path to forward slashes for logging config compat
    # (\Users would be mistaken for a unicode escape otherwise)
    str_log_file = str(log_file).replace("\\", "/")

    logging.config.fileConfig(
        ini_path,
        defaults={"log_file": str_log_file},
        disable_existing_loggers=False,
    )

    return log_file


def get_app_logger() -> logging.Logger:
    return logging.getLogger("bwmt.app")


def get_config_logger() -> logging.Logger:
    return logging.getLogger("bwmt.config")


def get_calibrate_logger() -> logging.Logger:
    return logging.getLogger("bwmt.calibrate")


def get_velocity_logger() -> logging.Logger:
    return logging.getLogger("bwmt.velocity")


def get_simulation_logger() -> logging.Logger:
    return logging.getLogger("bwmt.simulation")
