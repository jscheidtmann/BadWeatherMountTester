"""Configuration handling for Bad Weather Mount Tester."""

from dataclasses import dataclass, field
import json
from pathlib import Path

import yaml


@dataclass
class MountConfig:
    """Configuration for the mount being tested."""

    latitude: float = 0.0
    focal_length_mm: float = 200.0
    distance_to_screen_m: float = 5.0
    main_period_seconds: float = 480.0  # 8 minutes default for typical worm gear
    southern_hemisphere: bool = False


# Screen size presets
SCREEN_SIZE_PRESETS = {
    "640x480": (640, 480),
    "vga": (640, 480),
    "xga": (1024, 768),
    "hd": (1280, 720),
    "720p": (1280, 720),
    "fhd": (1920, 1080),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
    "2160p": (3840, 2160),
    "custom": None,  # Use screen_width and screen_height directly
}


@dataclass
class DisplayConfig:
    """Configuration for the display/simulator."""

    fullscreen: bool = True
    screen_size: str = "fhd"  # Preset: vga, hd/720p, fhd/1080p, 4k/2160p, or custom
    screen_width: int = 1920
    screen_height: int = 1080
    screen_width_mm: float = 527.0  # Physical screen width in mm (default: 24" monitor)
    star_size: float = 3.0  # Full Width at Half Maximum of simulated star in pixels
    star_brightness: int = 255
    target_y_ratio: float = 0.5  # Vertical position ratio for target crosshair (0=top, 1=bottom)

    def apply_screen_size_preset(self) -> None:
        """Apply screen size preset to screen_width and screen_height."""
        preset = self.screen_size.lower()
        if preset in SCREEN_SIZE_PRESETS:
            dimensions = SCREEN_SIZE_PRESETS[preset]
            if dimensions is not None:
                self.screen_width, self.screen_height = dimensions


@dataclass
class ServerConfig:
    """Configuration for the web server."""

    host: str = "0.0.0.0"
    port: int = 5000


@dataclass
class CameraConfig:
    """Configuration for the guiding camera."""

    pixel_size_um: float = 3.75  # Pixel size in micrometers
    width_px: int = 1280  # Sensor width in pixels
    height_px: int = 960  # Sensor height in pixels


@dataclass
class CalibrationConfig:
    """Configuration for the calibration trace line."""

    points: list = field(default_factory=list)  # List of [x, y] pairs
    is_complete: bool = False


@dataclass
class VelocityMeasurementConfig:
    """Configuration for velocity measurement results."""

    left_time_seconds: float | None = None
    middle_time_seconds: float | None = None
    right_time_seconds: float | None = None
    stripe_width_pixels: int = 0
    is_complete: bool = False


# Default path for setup configuration
DEFAULT_SETUP_PATH = Path("setup.yml")


@dataclass
class AppConfig:
    """Main application configuration."""

    mount: MountConfig = field(default_factory=MountConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    velocity: VelocityMeasurementConfig = field(default_factory=VelocityMeasurementConfig)

    def to_dict(self) -> dict:
        """Convert configuration to a dictionary."""
        return {
            "mount": {
                "latitude": self.mount.latitude,
                "focal_length_mm": self.mount.focal_length_mm,
                "distance_to_screen_m": self.mount.distance_to_screen_m,
                "main_period_seconds": self.mount.main_period_seconds,
                "southern_hemisphere": self.mount.southern_hemisphere,
            },
            "display": {
                "fullscreen": self.display.fullscreen,
                "screen_size": self.display.screen_size,
                "screen_width": self.display.screen_width,
                "screen_height": self.display.screen_height,
                "screen_width_mm": self.display.screen_width_mm,
                "star_size": self.display.star_size,
                "star_brightness": self.display.star_brightness,
                "target_y_ratio": self.display.target_y_ratio,
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
            },
            "camera": {
                "pixel_size_um": self.camera.pixel_size_um,
                "width_px": self.camera.width_px,
                "height_px": self.camera.height_px,
            },
            "calibration": {
                "points": self.calibration.points,
                "is_complete": self.calibration.is_complete,
            },
            "velocity": {
                "left_time_seconds": self.velocity.left_time_seconds,
                "middle_time_seconds": self.velocity.middle_time_seconds,
                "right_time_seconds": self.velocity.right_time_seconds,
                "stripe_width_pixels": self.velocity.stripe_width_pixels,
                "is_complete": self.velocity.is_complete,
            },
        }

    def save(self, path: Path) -> None:
        """Save configuration to a JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2))

    def save_yaml(self, path: Path = DEFAULT_SETUP_PATH) -> None:
        """Save configuration to a YAML file."""
        path.write_text(yaml.safe_dump(self.to_dict(), default_flow_style=False, sort_keys=False))

    @classmethod
    def _apply_dict(cls, config: "AppConfig", data: dict) -> None:
        """Apply dictionary values to a config object."""
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

        if "camera" in data:
            for key, value in data["camera"].items():
                if hasattr(config.camera, key):
                    setattr(config.camera, key, value)

        if "calibration" in data:
            for key, value in data["calibration"].items():
                if hasattr(config.calibration, key):
                    setattr(config.calibration, key, value)

        if "velocity" in data:
            for key, value in data["velocity"].items():
                if hasattr(config.velocity, key):
                    setattr(config.velocity, key, value)

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        """Load configuration from a JSON file."""
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        config = cls()
        cls._apply_dict(config, data)
        config.display.apply_screen_size_preset()
        return config

    @classmethod
    def load_yaml(cls, path: Path = DEFAULT_SETUP_PATH) -> "AppConfig":
        """Load configuration from a YAML file."""
        if not path.exists():
            return cls()

        data = yaml.safe_load(path.read_text())
        if data is None:
            return cls()

        config = cls()
        cls._apply_dict(config, data)
        config.display.apply_screen_size_preset()
        return config
