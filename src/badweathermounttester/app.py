"""Main application for Bad Weather Mount Tester."""

import argparse
import sys
from pathlib import Path

from badweathermounttester import __version__
from badweathermounttester.config import AppConfig, DEFAULT_SETUP_PATH
from badweathermounttester.display import SimulatorDisplay, DisplayMode
from badweathermounttester.server import WebServer


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
        # Step 3: Calibrate -> CALIBRATION
        # Step 4: Measure -> SIMULATION
        mode_map = {
            1: DisplayMode.LOCATOR,
            2: DisplayMode.ALIGN,
            3: DisplayMode.CALIBRATION,
            4: DisplayMode.SIMULATION,
        }
        if mode in mode_map:
            self.display.set_mode(mode_map[mode])

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
