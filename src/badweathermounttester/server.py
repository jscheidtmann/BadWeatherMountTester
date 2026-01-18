"""Web server component for Bad Weather Mount Tester.

This module provides the Flask-based web interface that allows
the Astro Computer to configure and control the simulator.
"""

import socket
from pathlib import Path
from threading import Thread
from typing import Optional, Callable

from flask import Flask, render_template, jsonify, request  # , g
from flask_babel import Babel  # , gettext as _

from badweathermounttester.config import AppConfig, DEFAULT_SETUP_PATH


def get_locale():
    """Select the best matching locale from the request."""
    return request.accept_languages.best_match(["en", "de", "fr", "es"])


class WebServer:
    """Flask web server for the BWMT control interface."""

    def __init__(self, config: AppConfig, setup_path: Path = DEFAULT_SETUP_PATH):
        self.config = config
        self.setup_path = setup_path
        package_dir = Path(__file__).parent
        self.app = Flask(
            __name__,
            template_folder=str(package_dir / "templates"),
            static_folder=str(package_dir / "static"),
        )

        # Configure Babel for internationalization
        self.app.config["BABEL_DEFAULT_LOCALE"] = "en"
        self.app.config["BABEL_TRANSLATION_DIRECTORIES"] = str(package_dir / "translations")
        self.babel = Babel(self.app, locale_selector=get_locale)

        # Make get_locale available in templates
        @self.app.context_processor
        def inject_locale():
            return {"get_locale": get_locale}

        self._setup_routes()
        self._server_thread: Optional[Thread] = None
        self._on_connect_callback: Optional[Callable[[], None]] = None
        self._on_config_update_callback: Optional[Callable[[AppConfig], None]] = None
        self._on_mode_change_callback: Optional[Callable[[int], None]] = None

    def _setup_routes(self) -> None:
        """Set up Flask routes."""

        @self.app.route("/")
        def index():
            if self._on_connect_callback:
                self._on_connect_callback()
            return render_template("index.html")

        @self.app.route("/api/config", methods=["GET"])
        def get_config():
            return jsonify(
                {
                    "mount": {
                        "latitude": self.config.mount.latitude,
                        "focal_length_mm": self.config.mount.focal_length_mm,
                        "distance_to_screen_m": self.config.mount.distance_to_screen_m,
                        "main_period_seconds": self.config.mount.main_period_seconds,
                    },
                    "display": {
                        "screen_width": self.config.display.screen_width,
                        "screen_height": self.config.display.screen_height,
                        "screen_width_mm": self.config.display.screen_width_mm,
                    },
                    "camera": {
                        "pixel_size_um": self.config.camera.pixel_size_um,
                        "width_px": self.config.camera.width_px,
                        "height_px": self.config.camera.height_px,
                    },
                }
            )

        @self.app.route("/api/config", methods=["POST"])
        def update_config():
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            if "mount" in data:
                mount_data = data["mount"]
                if "latitude" in mount_data:
                    self.config.mount.latitude = float(mount_data["latitude"])
                if "focal_length_mm" in mount_data:
                    self.config.mount.focal_length_mm = float(mount_data["focal_length_mm"])
                if "distance_to_screen_m" in mount_data:
                    self.config.mount.distance_to_screen_m = float(mount_data["distance_to_screen_m"])
                if "main_period_seconds" in mount_data:
                    self.config.mount.main_period_seconds = float(mount_data["main_period_seconds"])

            # Save to YAML file
            self.config.save_yaml(self.setup_path)

            if self._on_config_update_callback:
                self._on_config_update_callback(self.config)

            return jsonify({"status": "ok"})

        def _calculate_all_values():
            """Calculate all derived values from current config."""
            fl_m = self.config.mount.focal_length_mm / 1000  # Convert to meters
            dist = self.config.mount.distance_to_screen_m

            # Effective focal length
            if dist > fl_m and dist > 0 and self.config.mount.focal_length_mm > 0:
                effective_fl = (self.config.mount.focal_length_mm * dist) / (dist - fl_m)
            else:
                effective_fl = 0

            # Camera resolution in arcsec/pixel
            pixel_size_um = self.config.camera.pixel_size_um
            if effective_fl > 0 and pixel_size_um > 0:
                camera_resolution_arcsec = 206.265 * pixel_size_um / effective_fl
            else:
                camera_resolution_arcsec = 0

            # Binning calculation: 1 camera pixel should match ~10 simulator pixel
            # Camera pixel projected onto screen = (pixel_size_um * dist) / effective_fl mm
            # Screen pixel size = screen_width_mm / screen_width mm
            # binning = screen_pixel_size / camera_pixel_projected
            screen_width_mm = self.config.display.screen_width_mm
            screen_width_px = self.config.display.screen_width
            pixel_size_um = self.config.camera.pixel_size_um

            if effective_fl > 0 and pixel_size_um > 0 and dist > 0 and screen_width_px > 0:
                camera_pixel_on_screen = (pixel_size_um * dist) / effective_fl  # mm
                screen_pixel_size = screen_width_mm / screen_width_px  # mm
                recommended_binning = max(1, round(screen_pixel_size / 10.0 / camera_pixel_on_screen))
            else:
                recommended_binning = 1

            # Area on simulator (physical size in mm that the camera sees on the screen)
            # Sensor size in mm
            sensor_width_mm = (self.config.camera.width_px * self.config.camera.pixel_size_um) / 1000
            sensor_height_mm = (self.config.camera.height_px * self.config.camera.pixel_size_um) / 1000

            # Using lens equation: object_size = sensor_size * object_distance / focal_length
            # At close range with effective FL
            if effective_fl > 0:
                area_width_mm = (sensor_width_mm * dist * 1000) / effective_fl
                area_height_mm = (sensor_height_mm * dist * 1000) / effective_fl
            else:
                area_width_mm = 0
                area_height_mm = 0

            # Pixel pitch calculations
            if screen_width_mm > 0 and screen_width_px > 0:
                pixel_pitch_mm = screen_width_mm / screen_width_px
                if dist > 0:
                    # Angular size of one pixel as seen from mount (in arcsec)
                    pixel_pitch_arcsec = (pixel_pitch_mm / (dist * 1000)) * 206265
                else:
                    pixel_pitch_arcsec = 0
            else:
                pixel_pitch_mm = 0
                pixel_pitch_arcsec = 0

            # Duration in minutes
            duration_minutes = pixel_pitch_arcsec * screen_width_px / 15.0 / 60.0  # Assuming 15 arcsec/sec sidereal rate and convert to minutes

            return {
                "effective_focal_length": round(effective_fl, 1),
                "duration_minutes": round(duration_minutes, 1),
                "camera_resolution_arcsec": round(camera_resolution_arcsec, 2),
                "recommended_binning": recommended_binning,
                "area_width_mm": round(area_width_mm, 1),
                "area_height_mm": round(area_height_mm, 1),
                "pixel_pitch_mm": round(pixel_pitch_mm, 3),
                "pixel_pitch_arcsec": round(pixel_pitch_arcsec, 2),
            }

        @self.app.route("/api/config/mount/<field>", methods=["PATCH"])
        def update_mount_field(field: str):
            """Update a single mount configuration field."""
            data = request.get_json()
            if not data or "value" not in data:
                return jsonify({"error": "No value provided"}), 400

            valid_fields = ["latitude", "focal_length_mm", "distance_to_screen_m", "main_period_seconds"]
            if field not in valid_fields:
                return jsonify({"error": f"Invalid field: {field}"}), 400

            try:
                value = float(data["value"])
                setattr(self.config.mount, field, value)
            except (ValueError, TypeError) as e:
                return jsonify({"error": f"Invalid value: {e}"}), 400

            self.config.save_yaml(self.setup_path)

            if self._on_config_update_callback:
                self._on_config_update_callback(self.config)

            return jsonify({
                "status": "ok",
                "field": field,
                "value": value,
                "calculated": _calculate_all_values(),
            })

        @self.app.route("/api/config/camera/<field>", methods=["PATCH"])
        def update_camera_field(field: str):
            """Update a single camera configuration field."""
            data = request.get_json()
            if not data or "value" not in data:
                return jsonify({"error": "No value provided"}), 400

            valid_fields = ["pixel_size_um", "width_px", "height_px"]
            if field not in valid_fields:
                return jsonify({"error": f"Invalid field: {field}"}), 400

            try:
                if field in ["width_px", "height_px"]:
                    value = int(data["value"])
                else:
                    value = float(data["value"])
                setattr(self.config.camera, field, value)
            except (ValueError, TypeError) as e:
                return jsonify({"error": f"Invalid value: {e}"}), 400

            self.config.save_yaml(self.setup_path)

            if self._on_config_update_callback:
                self._on_config_update_callback(self.config)

            return jsonify({
                "status": "ok",
                "field": field,
                "value": value,
                "calculated": _calculate_all_values(),
            })

        @self.app.route("/api/config/display/<field>", methods=["PATCH"])
        def update_display_field(field: str):
            """Update a single display configuration field."""
            data = request.get_json()
            if not data or "value" not in data:
                return jsonify({"error": "No value provided"}), 400

            valid_fields = ["screen_width_mm"]
            if field not in valid_fields:
                return jsonify({"error": f"Invalid field: {field}"}), 400

            try:
                value = float(data["value"])
                setattr(self.config.display, field, value)
            except (ValueError, TypeError) as e:
                return jsonify({"error": f"Invalid value: {e}"}), 400

            self.config.save_yaml(self.setup_path)

            if self._on_config_update_callback:
                self._on_config_update_callback(self.config)

            return jsonify({
                "status": "ok",
                "field": field,
                "value": value,
                "calculated": _calculate_all_values(),
            })

        @self.app.route("/api/mode", methods=["POST"])
        def set_mode():
            data = request.get_json()
            if not data or "mode" not in data:
                return jsonify({"error": "Mode not specified"}), 400

            mode = int(data["mode"])
            if self._on_mode_change_callback:
                self._on_mode_change_callback(mode)

            return jsonify({"status": "ok", "mode": mode})

        @self.app.route("/api/calibration/click", methods=["POST"])
        def calibration_click():
            data = request.get_json()
            if not data or "x" not in data or "y" not in data:
                return jsonify({"error": "Coordinates not provided"}), 400
            # Calibration clicks will be handled by the main app
            return jsonify({"status": "ok", "x": data["x"], "y": data["y"]})

    def on_connect(self, callback: Callable[[], None]) -> None:
        """Set callback for when a client connects."""
        self._on_connect_callback = callback

    def on_config_update(self, callback: Callable[[AppConfig], None]) -> None:
        """Set callback for when configuration is updated."""
        self._on_config_update_callback = callback

    def on_mode_change(self, callback: Callable[[int], None]) -> None:
        """Set callback for when the UI mode changes."""
        self._on_mode_change_callback = callback

    def get_network_address(self) -> str:
        """Get the network address for clients to connect to."""
        hostname = socket.gethostname()
        try:
            # Try to get the actual IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = socket.gethostbyname(hostname)

        return f"http://{ip}:{self.config.server.port}"

    def start(self) -> None:
        """Start the web server in a background thread."""
        self._server_thread = Thread(
            target=self._run_server,
            daemon=True,
        )
        self._server_thread.start()

    def _run_server(self) -> None:
        """Run the Flask server."""
        self.app.run(
            host=self.config.server.host,
            port=self.config.server.port,
            debug=False,
            use_reloader=False,
        )

    def stop(self) -> None:
        """Stop the web server."""
        # Flask doesn't have a clean shutdown mechanism when run in a thread
        # The thread is daemonic, so it will be terminated when the main program exits
        pass
