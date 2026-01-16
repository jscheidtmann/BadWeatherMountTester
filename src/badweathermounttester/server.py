"""Web server component for Bad Weather Mount Tester.

This module provides the Flask-based web interface that allows
the Astro Computer to configure and control the simulator.
"""

import socket
from pathlib import Path
from threading import Thread
from typing import Optional, Callable

from flask import Flask, render_template, jsonify, request, g
from flask_babel import Babel, gettext as _

from badweathermounttester.config import AppConfig


def get_locale():
    """Select the best matching locale from the request."""
    return request.accept_languages.best_match(["en", "de", "fr", "es"])


class WebServer:
    """Flask web server for the BWMT control interface."""

    def __init__(self, config: AppConfig):
        self.config = config
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

            if self._on_config_update_callback:
                self._on_config_update_callback(self.config)

            return jsonify({"status": "ok"})

        @self.app.route("/api/mode", methods=["POST"])
        def set_mode():
            data = request.get_json()
            if not data or "mode" not in data:
                return jsonify({"error": "Mode not specified"}), 400
            # Mode changes will be handled by the main app
            return jsonify({"status": "ok", "mode": data["mode"]})

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
