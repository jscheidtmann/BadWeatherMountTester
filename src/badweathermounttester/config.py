"""Configuration handling for Bad Weather Mount Tester."""

from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path


@dataclass
class MountConfig:
    """Configuration for the mount being tested."""

    latitude: float = 0.0
    focal_length_mm: float = 200.0
    distance_to_screen_m: float = 5.0
    main_period_seconds: float = 480.0  # 8 minutes default for typical worm gear


@dataclass
class DisplayConfig:
    """Configuration for the display/simulator."""

    fullscreen: bool = True
    screen_width: int = 1920
    screen_height: int = 1080
    star_size: int = 5
    star_brightness: int = 255


@dataclass
class ServerConfig:
    """Configuration for the web server."""

    host: str = "0.0.0.0"
    port: int = 5000


@dataclass
class AppConfig:
    """Main application configuration."""

    mount: MountConfig = field(default_factory=MountConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    def save(self, path: Path) -> None:
        """Save configuration to a JSON file."""
        data = {
            "mount": {
                "latitude": self.mount.latitude,
                "focal_length_mm": self.mount.focal_length_mm,
                "distance_to_screen_m": self.mount.distance_to_screen_m,
                "main_period_seconds": self.mount.main_period_seconds,
            },
            "display": {
                "fullscreen": self.display.fullscreen,
                "screen_width": self.display.screen_width,
                "screen_height": self.display.screen_height,
                "star_size": self.display.star_size,
                "star_brightness": self.display.star_brightness,
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
            },
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        """Load configuration from a JSON file."""
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        config = cls()

        if "mount" in data:
            for key, value in data["mount"].items():
                if hasattr(config.mount, key):
                    setattr(config.mount, key, value)

        if "display" in data:
            for key, value in data["display"].items():
                if hasattr(config.display, key):
                    setattr(config.display, key, value)

        if "server" in data:
            for key, value in data["server"].items():
                if hasattr(config.server, key):
                    setattr(config.server, key, value)

        return config
