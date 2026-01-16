"""Main application for Bad Weather Mount Tester."""

import argparse
import sys
from pathlib import Path

from badweathermounttester import __version__
from badweathermounttester.config import AppConfig
from badweathermounttester.display import SimulatorDisplay, DisplayMode
from badweathermounttester.server import WebServer


class Application:
    """Main BWMT application that coordinates display and web server."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.display = SimulatorDisplay(config.display)
        self.server = WebServer(config)

        # Set up callbacks
        self.server.on_connect(self._on_client_connect)
        self.server.on_config_update(self._on_config_update)

    def _on_client_connect(self) -> None:
        """Handle client connection."""
        self.display.set_mode(DisplayMode.LOCATOR)

    def _on_config_update(self, config: AppConfig) -> None:
        """Handle configuration update."""
        self.config = config

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
        help="Path to configuration file",
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
    if args.config and args.config.exists():
        config = AppConfig.load(args.config)
    else:
        config = AppConfig()

    # Apply command line overrides
    if args.port:
        config.server.port = args.port
    if args.windowed:
        config.display.fullscreen = False

    # Run the application
    app = Application(config)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
