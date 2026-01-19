"""Web server component for Bad Weather Mount Tester.

This module provides the Flask-based web interface that allows
the Astro Computer to configure and control the simulator.
"""

import socket
from pathlib import Path
from threading import Thread
from typing import Optional, Callable, List

import numpy as np
from flask import Flask, render_template, jsonify, request  # , g
from flask_babel import Babel  # , gettext as _

from badweathermounttester.config import AppConfig, DEFAULT_SETUP_PATH


def fit_polynomial(points: List[List[int]], degree: int = 3) -> Optional[List[float]]:
    """Fit a polynomial to the calibration points. Returns coefficients [a, b, c, d] for ax³+bx²+cx+d."""
    if len(points) <= degree:
        return None
    x = np.array([p[0] for p in points], dtype=float)
    y = np.array([p[1] for p in points], dtype=float)
    try:
        coeffs = np.polyfit(x, y, degree)
        return [float(c) for c in coeffs]
    except (np.linalg.LinAlgError, ValueError):
        return None


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
        self._on_calibration_hover_callback: Optional[Callable[[int, int], None]] = None
        self._on_calibration_click_callback: Optional[Callable[[int, int], None]] = None
        self._on_calibration_select_callback: Optional[Callable[[int], None]] = None
        self._on_simulation_setup_callback: Optional[Callable[[int, int, float], None]] = None
        self._on_simulation_start_callback: Optional[Callable[[], None]] = None
        self._on_simulation_stop_callback: Optional[Callable[[], None]] = None
        self._on_simulation_reset_callback: Optional[Callable[[], None]] = None
        self._on_simulation_skip_callback: Optional[Callable[[float], None]] = None
        self._get_simulation_status_callback: Optional[Callable[[], dict]] = None

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

        @self.app.route("/api/calibration/hover", methods=["POST"])
        def calibration_hover():
            """Update the hover crosshair position for calibration."""
            data = request.get_json()
            if not data or "x" not in data or "y" not in data:
                return jsonify({"error": "Coordinates not provided"}), 400

            x = int(data["x"])
            y = int(data["y"])

            if self._on_calibration_hover_callback:
                self._on_calibration_hover_callback(x, y)

            return jsonify({"status": "ok", "x": x, "y": y})

        @self.app.route("/api/calibration/click", methods=["POST"])
        def calibration_click():
            """Record a calibration point."""
            data = request.get_json()
            if not data or "x" not in data or "y" not in data:
                return jsonify({"error": "Coordinates not provided"}), 400

            x = int(data["x"])
            y = int(data["y"])

            # Store the point in config
            self.config.calibration.points.append([x, y])
            self.config.save_yaml(self.setup_path)

            if self._on_calibration_click_callback:
                self._on_calibration_click_callback(x, y)

            # Compute polynomial fit if enough points
            poly_coeffs = fit_polynomial(self.config.calibration.points)

            return jsonify({
                "status": "ok",
                "x": x,
                "y": y,
                "points": self.config.calibration.points,
                "count": len(self.config.calibration.points),
                "polynomial": poly_coeffs,
            })

        @self.app.route("/api/calibration/points", methods=["GET"])
        def get_calibration_points():
            """Get all calibration points."""
            poly_coeffs = fit_polynomial(self.config.calibration.points)
            return jsonify({
                "points": self.config.calibration.points,
                "count": len(self.config.calibration.points),
                "is_complete": self.config.calibration.is_complete,
                "polynomial": poly_coeffs,
            })

        @self.app.route("/api/calibration/reset", methods=["DELETE"])
        def reset_calibration():
            """Clear all calibration points."""
            self.config.calibration.points = []
            self.config.calibration.is_complete = False
            self.config.save_yaml(self.setup_path)

            if self._on_calibration_click_callback:
                # Notify that calibration was reset by calling with special values
                self._on_calibration_click_callback(-1, -1)

            return jsonify({"status": "ok", "points": [], "count": 0})

        @self.app.route("/api/calibration/last", methods=["DELETE"])
        def delete_last_calibration_point():
            """Delete the last calibration point."""
            if self.config.calibration.points:
                self.config.calibration.points.pop()
                self.config.save_yaml(self.setup_path)

                if self._on_calibration_click_callback:
                    # Notify with special value to indicate deletion
                    self._on_calibration_click_callback(-2, -2)

            poly_coeffs = fit_polynomial(self.config.calibration.points)
            return jsonify({
                "status": "ok",
                "points": self.config.calibration.points,
                "count": len(self.config.calibration.points),
                "polynomial": poly_coeffs,
            })

        @self.app.route("/api/calibration/point/<int:index>", methods=["PATCH"])
        def update_calibration_point(index: int):
            """Update a specific calibration point's position."""
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            if index < 0 or index >= len(self.config.calibration.points):
                return jsonify({"error": "Invalid point index"}), 400

            # Handle relative movement (dx, dy) or absolute position (x, y)
            if "dx" in data or "dy" in data:
                dx = int(data.get("dx", 0))
                dy = int(data.get("dy", 0))
                self.config.calibration.points[index][0] += dx
                self.config.calibration.points[index][1] += dy
            elif "x" in data and "y" in data:
                self.config.calibration.points[index] = [int(data["x"]), int(data["y"])]
            else:
                return jsonify({"error": "Must provide dx/dy or x/y"}), 400

            self.config.save_yaml(self.setup_path)

            # Notify with the updated point coordinates
            if self._on_calibration_click_callback:
                self._on_calibration_click_callback(-3, index)  # -3 signals point update

            poly_coeffs = fit_polynomial(self.config.calibration.points)
            return jsonify({
                "status": "ok",
                "index": index,
                "point": self.config.calibration.points[index],
                "points": self.config.calibration.points,
                "polynomial": poly_coeffs,
            })

        @self.app.route("/api/calibration/select", methods=["POST"])
        def select_calibration_point():
            """Set the selected calibration point index."""
            data = request.get_json()
            if data is None or "index" not in data:
                return jsonify({"error": "Index not provided"}), 400

            index = int(data["index"])

            if self._on_calibration_select_callback:
                self._on_calibration_select_callback(index)

            return jsonify({"status": "ok", "index": index})

        @self.app.route("/api/simulation/setup", methods=["POST"])
        def simulation_setup():
            """Set up simulation parameters based on calibration data."""
            # Get x range from calibration points
            if len(self.config.calibration.points) < 4:
                return jsonify({"error": "Not enough calibration points"}), 400

            x_coords = [p[0] for p in self.config.calibration.points]
            x_start = min(x_coords)
            x_end = max(x_coords)

            # Calculate pixels per second based on sidereal rate
            # Sidereal rate is 15 arcsec/second
            # Pixel pitch in arcsec = (pixel_pitch_mm / distance_m / 1000) * 206265
            screen_width_mm = self.config.display.screen_width_mm
            screen_width_px = self.config.display.screen_width
            distance_m = self.config.mount.distance_to_screen_m

            if screen_width_mm <= 0 or screen_width_px <= 0 or distance_m <= 0:
                return jsonify({"error": "Invalid display/mount configuration"}), 400

            pixel_pitch_mm = screen_width_mm / screen_width_px
            pixel_pitch_arcsec = (pixel_pitch_mm / (distance_m * 1000)) * 206265
            pixels_per_second = 15.0 / pixel_pitch_arcsec  # 15 arcsec/sec sidereal rate

            if self._on_simulation_setup_callback:
                self._on_simulation_setup_callback(x_start, x_end, pixels_per_second)

            total_distance = x_end - x_start
            total_time = total_distance / pixels_per_second if pixels_per_second > 0 else 0

            return jsonify({
                "status": "ok",
                "x_start": x_start,
                "x_end": x_end,
                "pixels_per_second": round(pixels_per_second, 4),
                "total_seconds": round(total_time, 1),
            })

        @self.app.route("/api/simulation/start", methods=["POST"])
        def simulation_start():
            """Start or resume the simulation."""
            if self._on_simulation_start_callback:
                self._on_simulation_start_callback()
            return jsonify({"status": "ok"})

        @self.app.route("/api/simulation/stop", methods=["POST"])
        def simulation_stop():
            """Stop/pause the simulation."""
            if self._on_simulation_stop_callback:
                self._on_simulation_stop_callback()
            return jsonify({"status": "ok"})

        @self.app.route("/api/simulation/reset", methods=["POST"])
        def simulation_reset():
            """Reset the simulation to the beginning."""
            if self._on_simulation_reset_callback:
                self._on_simulation_reset_callback()
            return jsonify({"status": "ok"})

        @self.app.route("/api/simulation/skip", methods=["POST"])
        def simulation_skip():
            """Skip forward or backward by a number of seconds."""
            data = request.get_json()
            if not data or "seconds" not in data:
                return jsonify({"error": "Seconds not specified"}), 400

            seconds = float(data["seconds"])
            if self._on_simulation_skip_callback:
                self._on_simulation_skip_callback(seconds)
            return jsonify({"status": "ok", "skipped_seconds": seconds})

        @self.app.route("/api/simulation/status", methods=["GET"])
        def simulation_status():
            """Get current simulation status."""
            if self._get_simulation_status_callback:
                status = self._get_simulation_status_callback()
                return jsonify(status)
            return jsonify({
                "running": False,
                "progress": 0,
                "elapsed_seconds": 0,
                "remaining_seconds": 0,
                "complete": False,
            })

    def on_connect(self, callback: Callable[[], None]) -> None:
        """Set callback for when a client connects."""
        self._on_connect_callback = callback

    def on_config_update(self, callback: Callable[[AppConfig], None]) -> None:
        """Set callback for when configuration is updated."""
        self._on_config_update_callback = callback

    def on_mode_change(self, callback: Callable[[int], None]) -> None:
        """Set callback for when the UI mode changes."""
        self._on_mode_change_callback = callback

    def on_calibration_hover(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for when the calibration hover position changes."""
        self._on_calibration_hover_callback = callback

    def on_calibration_click(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for when a calibration point is clicked."""
        self._on_calibration_click_callback = callback

    def on_calibration_select(self, callback: Callable[[int], None]) -> None:
        """Set callback for when a calibration point is selected."""
        self._on_calibration_select_callback = callback

    def on_simulation_setup(self, callback: Callable[[int, int, float], None]) -> None:
        """Set callback for simulation setup (x_start, x_end, pixels_per_second)."""
        self._on_simulation_setup_callback = callback

    def on_simulation_start(self, callback: Callable[[], None]) -> None:
        """Set callback for simulation start."""
        self._on_simulation_start_callback = callback

    def on_simulation_stop(self, callback: Callable[[], None]) -> None:
        """Set callback for simulation stop."""
        self._on_simulation_stop_callback = callback

    def on_simulation_reset(self, callback: Callable[[], None]) -> None:
        """Set callback for simulation reset."""
        self._on_simulation_reset_callback = callback

    def on_simulation_skip(self, callback: Callable[[float], None]) -> None:
        """Set callback for simulation skip (seconds to skip, positive or negative)."""
        self._on_simulation_skip_callback = callback

    def set_simulation_status_getter(self, callback: Callable[[], dict]) -> None:
        """Set callback to get simulation status."""
        self._get_simulation_status_callback = callback

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
