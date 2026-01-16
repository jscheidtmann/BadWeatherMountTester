"""Tests for configuration handling."""

import json
import tempfile
from pathlib import Path

from badweathermounttester.config import AppConfig, MountConfig, DisplayConfig, ServerConfig


def test_default_config():
    """Test default configuration values."""
    config = AppConfig()
    assert config.mount.latitude == 0.0
    assert config.mount.focal_length_mm == 200.0
    assert config.mount.distance_to_screen_m == 5.0
    assert config.display.fullscreen is True
    assert config.server.port == 5000


def test_config_save_load():
    """Test saving and loading configuration."""
    config = AppConfig()
    config.mount.latitude = 51.5
    config.mount.focal_length_mm = 300.0
    config.server.port = 8080

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config.save(config_path)

        loaded_config = AppConfig.load(config_path)

        assert loaded_config.mount.latitude == 51.5
        assert loaded_config.mount.focal_length_mm == 300.0
        assert loaded_config.server.port == 8080


def test_config_load_nonexistent():
    """Test loading from a nonexistent file returns default config."""
    config = AppConfig.load(Path("/nonexistent/path/config.json"))
    assert config.mount.latitude == 0.0
    assert config.server.port == 5000
