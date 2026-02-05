"""Web server component for Bad Weather Mount Tester.

This module provides the Flask-based web interface that allows
the Astro Computer to configure and control the simulator.
"""

import socket
from pathlib import Path
from threading import Thread
from typing import Optional, Callable, List, Dict

import numpy as np
from flask import Flask, render_template, jsonify, request  # , g
from flask_babel import Babel  # , gettext as _
from waitress import serve

from badweathermounttester.config import AppConfig, DEFAULT_SETUP_PATH


def fit_ellipse(points: List[List[int]]) -> Optional[Dict]:
    """
    Fit an ellipse to the calibration points using least squares.

    Returns a dict with:
    - center_x, center_y: center of ellipse in pixels
    - semi_major: semi-major axis in pixels
    - semi_minor: semi-minor axis in pixels
    - angle: rotation angle in radians (from x-axis)
    - coeffs: [A, B, C, D, E, F] for general conic Ax²+Bxy+Cy²+Dx+Ey+F=0
    """
    if len(points) < 5:
        return None

    x = np.array([p[0] for p in points], dtype=float)
    y = np.array([p[1] for p in points], dtype=float)

    try:
        # Build design matrix for general conic: Ax² + Bxy + Cy² + Dx + Ey + F = 0
        # We use the constraint that it's an ellipse by using the direct least squares method
        D1 = np.vstack([x*x, x*y, y*y]).T
        D2 = np.vstack([x, y, np.ones_like(x)]).T

        S1 = D1.T @ D1
        S2 = D1.T @ D2
        S3 = D2.T @ D2

        # Constraint matrix for ellipse: 4AC - B² > 0
        C1 = np.array([[0, 0, 2], [0, -1, 0], [2, 0, 0]], dtype=float)

        # Solve the generalized eigenvalue problem
        S3_inv = np.linalg.inv(S3)
        M = np.linalg.inv(C1) @ (S1 - S2 @ S3_inv @ S2.T)

        eigenvalues, eigenvectors = np.linalg.eig(M)

        # Find the eigenvector corresponding to the positive eigenvalue
        # that satisfies the ellipse constraint
        cond = 4 * eigenvectors[0, :] * eigenvectors[2, :] - eigenvectors[1, :] ** 2
        valid_idx = np.where(cond > 0)[0]

        if len(valid_idx) == 0:
            return None

        # Take the one with smallest positive eigenvalue
        idx = valid_idx[np.argmin(np.abs(eigenvalues[valid_idx]))]
        a1 = eigenvectors[:, idx]
        a2 = -S3_inv @ S2.T @ a1

        # Coefficients [A, B, C, D, E, F]
        A, B, C = a1
        D, E, F = a2

        # Convert to geometric parameters
        # Center: solve dF/dx = 0, dF/dy = 0
        # 2Ax + By + D = 0
        # Bx + 2Cy + E = 0
        denom = 4 * A * C - B * B
        if abs(denom) < 1e-10:
            return None

        center_x = (B * E - 2 * C * D) / denom
        center_y = (B * D - 2 * A * E) / denom

        # Calculate semi-axes and rotation angle
        # Using formulas from conic section theory
        num = 2 * (A * E * E + C * D * D - B * D * E + (B * B - 4 * A * C) * F)
        term1 = A + C
        term2 = np.sqrt((A - C) ** 2 + B ** 2)

        denom_a = (B * B - 4 * A * C) * (term2 - (A + C))
        denom_b = (B * B - 4 * A * C) * (-term2 - (A + C))

        if denom_a == 0 or denom_b == 0 or num / denom_a < 0 or num / denom_b < 0:
            return None

        semi_major = np.sqrt(num / denom_a)
        semi_minor = np.sqrt(num / denom_b)

        # Ensure semi_major >= semi_minor
        if semi_minor > semi_major:
            semi_major, semi_minor = semi_minor, semi_major

        # Rotation angle
        if abs(B) < 1e-10:
            angle = 0 if A < C else np.pi / 2
        else:
            angle = np.arctan2(C - A - term2, B)

        return {
            "center_x": float(center_x),
            "center_y": float(center_y),
            "semi_major": float(semi_major),
            "semi_minor": float(semi_minor),
            "angle": float(angle),
            "coeffs": [float(A), float(B), float(C), float(D), float(E), float(F)],
        }

    except (np.linalg.LinAlgError, ValueError, ZeroDivisionError):
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
        self._on_simulation_setup_callback: Optional[Callable[[int, int, float, Optional[list]], None]] = None
        self._on_simulation_start_callback: Optional[Callable[[], None]] = None
        self._on_simulation_stop_callback: Optional[Callable[[], None]] = None
        self._on_simulation_reset_callback: Optional[Callable[[], None]] = None
        self._on_simulation_skip_callback: Optional[Callable[[float], None]] = None
        self._on_simulation_seek_callback: Optional[Callable[[float], None]] = None
        self._get_simulation_status_callback: Optional[Callable[[], dict]] = None
        self._on_velocity_setup_callback: Optional[Callable[[float], None]] = None
        self._get_velocity_stripe_width_callback: Optional[Callable[[], int]] = None

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

            # Adjust for latitude: star moves slower by factor cos(90° - latitude) = sin(latitude)
            latitude = abs(self.config.mount.latitude)
            if latitude != 0:
                latitude_factor = np.cos(np.radians(90.0 - latitude))
                if latitude_factor > 0:
                    duration_minutes /= latitude_factor

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

            # Store the point in config and sort by x coordinate
            self.config.calibration.points.append([x, y])
            self.config.calibration.points.sort(key=lambda p: p[0])
            self.config.save_yaml(self.setup_path)

            # Find the new index of the added point after sorting
            new_index = next(
                i for i, p in enumerate(self.config.calibration.points)
                if p[0] == x and p[1] == y
            )

            if self._on_calibration_click_callback:
                self._on_calibration_click_callback(x, y)

            # Compute ellipse fit if enough points
            ellipse_params = fit_ellipse(self.config.calibration.points)

            return jsonify({
                "status": "ok",
                "x": x,
                "y": y,
                "points": self.config.calibration.points,
                "count": len(self.config.calibration.points),
                "new_index": new_index,
                "ellipse": ellipse_params,
            })

        @self.app.route("/api/calibration/points", methods=["GET"])
        def get_calibration_points():
            """Get all calibration points."""
            ellipse_params = fit_ellipse(self.config.calibration.points)
            return jsonify({
                "points": self.config.calibration.points,
                "count": len(self.config.calibration.points),
                "is_complete": self.config.calibration.is_complete,
                "ellipse": ellipse_params,
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

        @self.app.route("/api/calibration/point/<int:index>", methods=["DELETE"])
        def delete_calibration_point(index: int):
            """Delete a calibration point by index."""
            if index < 0 or index >= len(self.config.calibration.points):
                return jsonify({"error": "Invalid point index"}), 400

            del self.config.calibration.points[index]
            self.config.save_yaml(self.setup_path)

            if self._on_calibration_click_callback:
                # Notify with special value to indicate deletion (-2, index)
                self._on_calibration_click_callback(-2, index)

            ellipse_params = fit_ellipse(self.config.calibration.points)
            return jsonify({
                "status": "ok",
                "points": self.config.calibration.points,
                "count": len(self.config.calibration.points),
                "ellipse": ellipse_params,
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

            ellipse_params = fit_ellipse(self.config.calibration.points)
            return jsonify({
                "status": "ok",
                "index": index,
                "point": self.config.calibration.points[index],
                "points": self.config.calibration.points,
                "ellipse": ellipse_params,
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

            # Calculate theoretical pixels per second based on sidereal rate
            # Sidereal rate is 15 arcsec/second
            # Pixel pitch in arcsec = (pixel_pitch_mm / distance_m / 1000) * 206265
            screen_width_mm = self.config.display.screen_width_mm
            screen_width_px = self.config.display.screen_width
            distance_m = self.config.mount.distance_to_screen_m

            if screen_width_mm <= 0 or screen_width_px <= 0 or distance_m <= 0:
                return jsonify({"error": "Invalid display/mount configuration"}), 400

            pixel_pitch_mm = screen_width_mm / screen_width_px
            pixel_pitch_arcsec = (pixel_pitch_mm / (distance_m * 1000)) * 206265
            calculated_pixels_per_second = 15.0 / pixel_pitch_arcsec  # 15 arcsec/sec sidereal rate

            # Reduce velocity by cos(90° - latitude) = sin(latitude)
            # At higher latitudes, stars move more slowly across the sky
            latitude = abs(self.config.mount.latitude)
            if latitude != 0:
                latitude_factor = np.cos(np.radians(90.0 - latitude))
                calculated_pixels_per_second *= latitude_factor

            # Check if we have measured velocity data to use instead
            velocity_source = "calculated"
            pixels_per_second = calculated_pixels_per_second
            velocity_profile = None

            if (self.config.velocity.is_complete
                    and self.config.velocity.stripe_width_pixels > 0
                    and self.config.velocity.left_time_seconds is not None
                    and self.config.velocity.middle_time_seconds is not None
                    and self.config.velocity.right_time_seconds is not None):
                stripe_width = self.config.velocity.stripe_width_pixels
                screen_width = self.config.display.screen_width

                # Compute per-stripe velocities at stripe center positions
                v_left = stripe_width / self.config.velocity.left_time_seconds if self.config.velocity.left_time_seconds > 0 else 0
                v_mid = stripe_width / self.config.velocity.middle_time_seconds if self.config.velocity.middle_time_seconds > 0 else 0
                v_right = stripe_width / self.config.velocity.right_time_seconds if self.config.velocity.right_time_seconds > 0 else 0

                # Stripe center x-positions (same layout as display.py)
                x_left = stripe_width / 2.0
                x_mid = screen_width / 2.0
                x_right = screen_width - stripe_width / 2.0

                # Use max velocity as the representative constant velocity
                pixels_per_second = max(v_left, v_mid, v_right)
                velocity_profile = [(x_left, v_left), (x_mid, v_mid), (x_right, v_right)]
                velocity_source = "measured_interpolated"

            if self._on_simulation_setup_callback:
                self._on_simulation_setup_callback(x_start, x_end, pixels_per_second, velocity_profile)

            # Get total_seconds from the display's simulation status after setup
            if self._get_simulation_status_callback:
                status = self._get_simulation_status_callback()
                total_time = status.get("total_seconds", 0)
            else:
                total_distance = x_end - x_start
                total_time = total_distance / pixels_per_second if pixels_per_second > 0 else 0

            return jsonify({
                "status": "ok",
                "x_start": x_start,
                "x_end": x_end,
                "pixels_per_second": round(pixels_per_second, 4),
                "calculated_pixels_per_second": round(calculated_pixels_per_second, 4),
                "velocity_source": velocity_source,
                "total_seconds": round(total_time, 1),
            })

        @self.app.route("/api/simulation/velocity", methods=["GET"])
        def simulation_velocity():
            """Get simulation velocity without side effects."""
            # Get x range from calibration points
            if len(self.config.calibration.points) < 4:
                return jsonify({"error": "Not enough calibration points"}), 400

            x_coords = [p[0] for p in self.config.calibration.points]
            x_start = min(x_coords)
            x_end = max(x_coords)

            # Calculate theoretical pixels per second based on sidereal rate
            screen_width_mm = self.config.display.screen_width_mm
            screen_width_px = self.config.display.screen_width
            distance_m = self.config.mount.distance_to_screen_m

            if screen_width_mm <= 0 or screen_width_px <= 0 or distance_m <= 0:
                return jsonify({"error": "Invalid display/mount configuration"}), 400

            pixel_pitch_mm = screen_width_mm / screen_width_px
            pixel_pitch_arcsec = (pixel_pitch_mm / (distance_m * 1000)) * 206265
            calculated_pixels_per_second = 15.0 / pixel_pitch_arcsec

            # Reduce velocity by cos(90° - latitude) = sin(latitude)
            latitude = abs(self.config.mount.latitude)
            if latitude != 0:
                latitude_factor = np.cos(np.radians(90.0 - latitude))
                calculated_pixels_per_second *= latitude_factor

            # Check if we have measured velocity data
            velocity_source = "calculated"
            pixels_per_second = calculated_pixels_per_second

            if (self.config.velocity.is_complete
                    and self.config.velocity.stripe_width_pixels > 0
                    and self.config.velocity.left_time_seconds is not None
                    and self.config.velocity.middle_time_seconds is not None
                    and self.config.velocity.right_time_seconds is not None):
                stripe_width = self.config.velocity.stripe_width_pixels
                screen_width = self.config.display.screen_width

                # Compute per-stripe velocities at stripe center positions
                v_left = stripe_width / self.config.velocity.left_time_seconds if self.config.velocity.left_time_seconds > 0 else 0
                v_mid = stripe_width / self.config.velocity.middle_time_seconds if self.config.velocity.middle_time_seconds > 0 else 0
                v_right = stripe_width / self.config.velocity.right_time_seconds if self.config.velocity.right_time_seconds > 0 else 0

                # Stripe center x-positions
                x_left = stripe_width / 2.0
                x_mid = screen_width / 2.0
                x_right = screen_width - stripe_width / 2.0

                # Use max velocity as the representative constant velocity
                pixels_per_second = max(v_left, v_mid, v_right)
                velocity_source = "measured_interpolated"

                # Compute total time via numerical integration (quadratic polynomial)
                profile_xs = np.array([x_left, x_mid, x_right])
                profile_vs = np.array([v_left, v_mid, v_right])
                coeffs = np.polyfit(profile_xs, profile_vs, 2)
                lookup_xs = np.linspace(float(x_start), float(x_end), 1000)
                lookup_vs = np.maximum(np.polyval(coeffs, lookup_xs), 0.01)
                dx = np.diff(lookup_xs)
                avg_vs = (lookup_vs[:-1] + lookup_vs[1:]) / 2.0
                dt = dx / avg_vs
                total_time = float(np.sum(dt))
            else:
                total_distance = x_end - x_start
                total_time = total_distance / pixels_per_second if pixels_per_second > 0 else 0

            return jsonify({
                "x_start": x_start,
                "x_end": x_end,
                "pixels_per_second": round(pixels_per_second, 4),
                "calculated_pixels_per_second": round(calculated_pixels_per_second, 4),
                "velocity_source": velocity_source,
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

        @self.app.route("/api/simulation/seek", methods=["POST"])
        def simulation_seek():
            """Seek to a specific elapsed time in the simulation."""
            data = request.get_json()
            if not data or "elapsed_seconds" not in data:
                return jsonify({"error": "elapsed_seconds not specified"}), 400

            elapsed_seconds = float(data["elapsed_seconds"])
            if self._on_simulation_seek_callback:
                self._on_simulation_seek_callback(elapsed_seconds)
            return jsonify({"status": "ok", "elapsed_seconds": elapsed_seconds})

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

        @self.app.route("/api/velocity", methods=["GET"])
        def get_velocity():
            """Get current velocity measurements."""
            return jsonify({
                "left_time_seconds": self.config.velocity.left_time_seconds,
                "middle_time_seconds": self.config.velocity.middle_time_seconds,
                "right_time_seconds": self.config.velocity.right_time_seconds,
                "stripe_width_pixels": self.config.velocity.stripe_width_pixels,
                "is_complete": self.config.velocity.is_complete,
            })

        @self.app.route("/api/velocity/setup", methods=["POST"])
        def velocity_setup():
            """Set up velocity measurement display."""
            # Calculate pixels per second based on sidereal rate
            screen_width_mm = self.config.display.screen_width_mm
            screen_width_px = self.config.display.screen_width
            distance_m = self.config.mount.distance_to_screen_m

            if screen_width_mm <= 0 or screen_width_px <= 0 or distance_m <= 0:
                return jsonify({"error": "Invalid display/mount configuration"}), 400

            pixel_pitch_mm = screen_width_mm / screen_width_px
            pixel_pitch_arcsec = (pixel_pitch_mm / (distance_m * 1000)) * 206265
            pixels_per_second = 15.0 / pixel_pitch_arcsec  # 15 arcsec/sec sidereal rate

            # Reduce velocity by cos(90° - latitude) = sin(latitude)
            latitude = abs(self.config.mount.latitude)
            if latitude != 0:
                latitude_factor = np.cos(np.radians(90.0 - latitude))
                pixels_per_second *= latitude_factor

            # Calculate stripe width for ~3 minutes crossing time
            stripe_width = int(pixels_per_second * 180)
            if stripe_width < 50:
                stripe_width = 50

            # Store in config
            self.config.velocity.stripe_width_pixels = stripe_width
            self.config.save_yaml(self.setup_path)

            if self._on_velocity_setup_callback:
                self._on_velocity_setup_callback(pixels_per_second)

            return jsonify({
                "status": "ok",
                "pixels_per_second": round(pixels_per_second, 4),
                "stripe_width_pixels": stripe_width,
                "expected_crossing_seconds": round(stripe_width / pixels_per_second, 1) if pixels_per_second > 0 else 0,
            })

        @self.app.route("/api/velocity/time", methods=["POST"])
        def record_velocity_time():
            """Record a velocity measurement time."""
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            stripe = data.get("stripe")
            time_seconds = data.get("time_seconds")

            if stripe not in ["left", "middle", "right"]:
                return jsonify({"error": "Invalid stripe (must be left, middle, or right)"}), 400

            if time_seconds is None or time_seconds < 0:
                return jsonify({"error": "Invalid time_seconds"}), 400

            # Store the measurement
            if stripe == "left":
                self.config.velocity.left_time_seconds = float(time_seconds)
            elif stripe == "middle":
                self.config.velocity.middle_time_seconds = float(time_seconds)
            elif stripe == "right":
                self.config.velocity.right_time_seconds = float(time_seconds)

            # Check if all measurements are complete
            self.config.velocity.is_complete = (
                self.config.velocity.left_time_seconds is not None
                and self.config.velocity.middle_time_seconds is not None
                and self.config.velocity.right_time_seconds is not None
            )

            self.config.save_yaml(self.setup_path)

            return jsonify({
                "status": "ok",
                "stripe": stripe,
                "time_seconds": time_seconds,
                "is_complete": self.config.velocity.is_complete,
            })

        @self.app.route("/api/velocity/time/<stripe>", methods=["DELETE"])
        def clear_velocity_time(stripe: str):
            """Clear a velocity measurement time."""
            if stripe not in ["left", "middle", "right"]:
                return jsonify({"error": "Invalid stripe"}), 400

            # Clear the measurement
            if stripe == "left":
                self.config.velocity.left_time_seconds = None
            elif stripe == "middle":
                self.config.velocity.middle_time_seconds = None
            elif stripe == "right":
                self.config.velocity.right_time_seconds = None

            # Update is_complete flag
            self.config.velocity.is_complete = False
            self.config.save_yaml(self.setup_path)

            return jsonify({"status": "ok", "stripe": stripe})

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

    def on_simulation_setup(self, callback: Callable[[int, int, float, Optional[list]], None]) -> None:
        """Set callback for simulation setup (x_start, x_end, pixels_per_second, velocity_profile)."""
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

    def on_simulation_seek(self, callback: Callable[[float], None]) -> None:
        """Set callback for simulation seek (elapsed seconds to seek to)."""
        self._on_simulation_seek_callback = callback

    def set_simulation_status_getter(self, callback: Callable[[], dict]) -> None:
        """Set callback to get simulation status."""
        self._get_simulation_status_callback = callback

    def on_velocity_setup(self, callback: Callable[[float], None]) -> None:
        """Set callback for velocity measurement setup (pixels_per_second)."""
        self._on_velocity_setup_callback = callback

    def set_velocity_stripe_width_getter(self, callback: Callable[[], int]) -> None:
        """Set callback to get velocity stripe width."""
        self._get_velocity_stripe_width_callback = callback

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
        """Run the Flask server using waitress."""
        serve(
            self.app,
            host=self.config.server.host,
            port=self.config.server.port,
        )

    def stop(self) -> None:
        """Stop the web server."""
        # Flask doesn't have a clean shutdown mechanism when run in a thread
        # The thread is daemonic, so it will be terminated when the main program exits
        pass
