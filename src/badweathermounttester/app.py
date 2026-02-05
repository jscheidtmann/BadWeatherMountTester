"""Main application for Bad Weather Mount Tester."""

import argparse
import sys
from pathlib import Path

from badweathermounttester import __version__
from typing import Optional, List, Tuple

from badweathermounttester.config import AppConfig, DEFAULT_SETUP_PATH
from badweathermounttester.display import SimulatorDisplay, DisplayMode
from badweathermounttester.server import WebServer, fit_ellipse


class Application:
    """Main BWMT application that coordinates display and web server."""

    def __init__(self, config: AppConfig, setup_path: Path = DEFAULT_SETUP_PATH):
        self.config = config
        self.setup_path = setup_path
        self.display = SimulatorDisplay(config.display)
        self.server = WebServer(config, setup_path)

        # Set up callbacks
        self.server.on_connect(self._on_client_connect)
        self.server.on_config_update(self._on_config_update)
        self.server.on_mode_change(self._on_mode_change)
        self.server.on_calibration_hover(self._on_calibration_hover)
        self.server.on_calibration_click(self._on_calibration_click)
        self.server.on_calibration_select(self._on_calibration_select)
        self.server.on_simulation_setup(self._on_simulation_setup)
        self.server.on_simulation_start(self._on_simulation_start)
        self.server.on_simulation_stop(self._on_simulation_stop)
        self.server.on_simulation_reset(self._on_simulation_reset)
        self.server.on_simulation_skip(self._on_simulation_skip)
        self.server.on_simulation_seek(self._on_simulation_seek)
        self.server.set_simulation_status_getter(self._get_simulation_status)
        self.server.on_velocity_setup(self._on_velocity_setup)

    def _on_client_connect(self) -> None:
        """Handle client connection."""
        self.display.set_mode(DisplayMode.LOCATOR)

    def _on_config_update(self, config: AppConfig) -> None:
        """Handle configuration update."""
        self.config = config

    def _on_mode_change(self, mode: int) -> None:
        """Handle UI mode change from web interface."""
        # Map UI step numbers to display modes
        # Step 1: Configure -> LOCATOR
        # Step 2: Align -> ALIGN (horizontal lines)
        # Step 3: Calibrate -> CALIBRATION (add, update, remove points)
        # Step 4: Velocity -> VELOCITY_MEASURE (measure velocity on screen)
        # Step 5: Measure -> SIMULATION (simulate star movement for mount to track)
        mode_map = {
            1: DisplayMode.LOCATOR,
            2: DisplayMode.ALIGN,
            3: DisplayMode.CALIBRATION,
            4: DisplayMode.VELOCITY_MEASURE,
            5: DisplayMode.SIMULATION,
        }
        if mode in mode_map:
            self.display.set_mode(mode_map[mode])

            # When entering calibration mode, initialize points from config
            if mode == 3:
                points = [(p[0], p[1]) for p in self.config.calibration.points]
                self.display.set_calibration_points(points)
                self._update_calibration_ellipse()

            # When entering velocity measurement mode, initialize calibration points and ellipse
            if mode == 4:
                points = [(p[0], p[1]) for p in self.config.calibration.points]
                self.display.set_calibration_points(points)
                ellipse = fit_ellipse(self.config.calibration.points)
                self.display.set_calibration_ellipse(ellipse)

            # When entering simulation mode, initialize calibration points and ellipse
            if mode == 5:
                points = [(p[0], p[1]) for p in self.config.calibration.points]
                self.display.set_calibration_points(points)
                ellipse = fit_ellipse(self.config.calibration.points)
                self.display.set_calibration_ellipse(ellipse)

    def _on_calibration_hover(self, x: int, y: int) -> None:
        """Handle calibration hover position change."""
        self.display.set_calibration_hover(x, y)

    def _update_calibration_ellipse(self) -> None:
        """Recompute and update the ellipse fit for calibration points."""
        ellipse = fit_ellipse(self.display.calibration_points)
        self.display.set_calibration_ellipse(ellipse)

    def _sync_calibration_from_config(self) -> None:
        """Sync display calibration points from config to ensure consistency."""
        points = [(p[0], p[1]) for p in self.config.calibration.points]
        self.display.set_calibration_points(points)
        # Adjust selected index if needed
        if self.display.calibration_selected_index >= len(self.display.calibration_points):
            self.display.calibration_selected_index = len(self.display.calibration_points) - 1
        self._update_calibration_ellipse()

    def _on_calibration_click(self, x: int, y: int) -> None:
        """Handle calibration point click."""
        if x == -1 and y == -1:
            # Reset signal
            self.display.clear_calibration_points()
        elif x == -2:
            # Delete selected signal - reload from config to ensure sync
            self._sync_calibration_from_config()
        elif x == -3:
            # Point update signal - reload from config to ensure sync
            self._sync_calibration_from_config()
        else:
            # Add point - reload from config to ensure sync
            self._sync_calibration_from_config()

    def _on_calibration_select(self, index: int) -> None:
        """Handle calibration point selection."""
        self.display.set_calibration_selected_index(index)

    def _on_velocity_setup(self, pixels_per_second: float) -> None:
        """Handle velocity measurement setup."""
        # Make sure ellipse is set from calibration points
        ellipse = fit_ellipse(self.config.calibration.points)
        self.display.set_calibration_ellipse(ellipse)
        self.display.setup_velocity_measurement(pixels_per_second)

    def _on_simulation_setup(self, x_start: int, x_end: int, pixels_per_second: float,
                             velocity_profile: Optional[List[Tuple[float, float]]] = None) -> None:
        """Handle simulation setup."""
        # Make sure ellipse is set from calibration points
        ellipse = fit_ellipse(self.config.calibration.points)
        self.display.set_calibration_ellipse(ellipse)
        self.display.setup_simulation(x_start, x_end, pixels_per_second, velocity_profile)

    def _on_simulation_start(self) -> None:
        """Handle simulation start."""
        self.display.start_simulation()

    def _on_simulation_stop(self) -> None:
        """Handle simulation stop."""
        self.display.stop_simulation()

    def _on_simulation_reset(self) -> None:
        """Handle simulation reset."""
        self.display.reset_simulation()

    def _on_simulation_skip(self, seconds: float) -> None:
        """Handle simulation skip."""
        self.display.skip_simulation(seconds)

    def _on_simulation_seek(self, elapsed_seconds: float) -> None:
        """Handle simulation seek to specific time."""
        self.display.seek_simulation(elapsed_seconds)

    def _get_simulation_status(self) -> dict:
        """Get current simulation status from display."""
        return self.display.get_simulation_status()

    def run(self) -> int:
        """Run the application. Returns exit code."""
        try:
            # Initialize display
            self.display.init()

            # Start web server
            self.server.start()
            network_address = self.server.get_network_address()
            self.display.set_network_address(network_address)

            print(f"BWMT started. Connect to: {network_address}")

            # Main loop
            while self.display.running:
                if not self.display.handle_events():
                    break
                self.display.render()
                self.display.clock.tick(60)  # 60 FPS

            return 0

        except KeyboardInterrupt:
            print("\nShutting down...")
            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        finally:
            self.display.quit()
            self.server.stop()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="bwmt",
        description="Bad Weather Mount Tester - Test telescope mount periodic error indoors",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file (JSON)",
    )
    parser.add_argument(
        "--setup",
        type=Path,
        default=DEFAULT_SETUP_PATH,
        help="Path to setup file (YAML, default: setup.yml)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Web server port (default: 5000)",
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Run in windowed mode instead of fullscreen",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Load or create configuration
    # Priority: --config (JSON) > --setup (YAML) > defaults
    if args.config and args.config.exists():
        config = AppConfig.load(args.config)
    elif args.setup.exists():
        config = AppConfig.load_yaml(args.setup)
    else:
        config = AppConfig()

    # Apply command line overrides
    if args.port:
        config.server.port = args.port
    if args.windowed:
        config.display.fullscreen = False

    # Run the application
    app = Application(config, args.setup)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
