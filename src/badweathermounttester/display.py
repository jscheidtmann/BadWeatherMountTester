"""Display/Simulator component for Bad Weather Mount Tester.

This module handles the pygame-based display that shows:
- The BWMT logo and waiting screen
- The locator screen for finding the screen with the guide scope
- The simulated star for guiding
"""

import pygame
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Tuple

from badweathermounttester.config import DisplayConfig


class DisplayMode(Enum):
    """Current display mode."""

    WAITING = auto()
    LOCATOR = auto()
    CALIBRATION = auto()
    SIMULATION = auto()


@dataclass
class StarPosition:
    """Position of the simulated star."""

    x: float
    y: float


class SimulatorDisplay:
    """Manages the pygame display for the simulator."""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.mode = DisplayMode.WAITING
        self.star_position: Optional[StarPosition] = None
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.running = False
        self.network_address: str = ""

    def init(self) -> None:
        """Initialize pygame and create the display."""
        pygame.init()
        pygame.display.set_caption("Bad Weather Mount Tester")

        if self.config.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            info = pygame.display.Info()
            self.config.screen_width = info.current_w
            self.config.screen_height = info.current_h
        else:
            self.screen = pygame.display.set_mode(
                (self.config.screen_width, self.config.screen_height)
            )

        self.clock = pygame.time.Clock()
        self.running = True

    def set_network_address(self, address: str) -> None:
        """Set the network address to display on the waiting screen."""
        self.network_address = address

    def set_mode(self, mode: DisplayMode) -> None:
        """Change the display mode."""
        self.mode = mode

    def set_star_position(self, x: float, y: float) -> None:
        """Set the position of the simulated star."""
        self.star_position = StarPosition(x, y)

    def handle_events(self) -> bool:
        """Process pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
        return True

    def render(self) -> None:
        """Render the current display mode."""
        if not self.screen:
            return

        self.screen.fill((0, 0, 0))

        if self.mode == DisplayMode.WAITING:
            self._render_waiting()
        elif self.mode == DisplayMode.LOCATOR:
            self._render_locator()
        elif self.mode == DisplayMode.CALIBRATION:
            self._render_calibration()
        elif self.mode == DisplayMode.SIMULATION:
            self._render_simulation()

        pygame.display.flip()

    def _render_waiting(self) -> None:
        """Render the waiting screen with logo and network address."""
        if not self.screen:
            return

        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)

        # Title
        title = font_large.render("Bad Weather Mount Tester", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.config.screen_width // 2, 150))
        self.screen.blit(title, title_rect)

        # Status
        status = font_medium.render("Waiting for connection...", True, (200, 200, 200))
        status_rect = status.get_rect(center=(self.config.screen_width // 2, 300))
        self.screen.blit(status, status_rect)

        # Network address
        if self.network_address:
            addr_text = font_medium.render(
                f"Connect to: {self.network_address}", True, (100, 255, 100)
            )
            addr_rect = addr_text.get_rect(center=(self.config.screen_width // 2, 400))
            self.screen.blit(addr_text, addr_rect)

        # Instructions
        instructions = font_small.render(
            "Press ESC to exit", True, (150, 150, 150)
        )
        instr_rect = instructions.get_rect(
            center=(self.config.screen_width // 2, self.config.screen_height - 50)
        )
        self.screen.blit(instructions, instr_rect)

    def _render_locator(self) -> None:
        """Render the locator screen with crosshairs and grid."""
        if not self.screen:
            return

        width = self.config.screen_width
        height = self.config.screen_height
        center_x = width // 2
        center_y = height // 2

        # Draw grid
        grid_color = (50, 50, 50)
        for x in range(0, width, 100):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, height))
        for y in range(0, height, 100):
            pygame.draw.line(self.screen, grid_color, (0, y), (width, y))

        # Draw center crosshair
        crosshair_color = (255, 0, 0)
        pygame.draw.line(self.screen, crosshair_color, (center_x - 50, center_y), (center_x + 50, center_y), 2)
        pygame.draw.line(self.screen, crosshair_color, (center_x, center_y - 50), (center_x, center_y + 50), 2)

        # Draw corner markers
        marker_color = (0, 255, 0)
        marker_size = 30
        # Top-left
        pygame.draw.line(self.screen, marker_color, (0, 0), (marker_size, 0), 2)
        pygame.draw.line(self.screen, marker_color, (0, 0), (0, marker_size), 2)
        # Top-right
        pygame.draw.line(self.screen, marker_color, (width - marker_size, 0), (width, 0), 2)
        pygame.draw.line(self.screen, marker_color, (width - 1, 0), (width - 1, marker_size), 2)
        # Bottom-left
        pygame.draw.line(self.screen, marker_color, (0, height - 1), (marker_size, height - 1), 2)
        pygame.draw.line(self.screen, marker_color, (0, height - marker_size), (0, height), 2)
        # Bottom-right
        pygame.draw.line(self.screen, marker_color, (width - marker_size, height - 1), (width, height - 1), 2)
        pygame.draw.line(self.screen, marker_color, (width - 1, height - marker_size), (width - 1, height), 2)

    def _render_calibration(self) -> None:
        """Render the calibration screen with arrows pointing to corners."""
        if not self.screen:
            return

        # For now, just show a simple calibration pattern
        self._render_locator()

        font = pygame.font.Font(None, 36)
        text = font.render("Calibration Mode", True, (255, 255, 0))
        text_rect = text.get_rect(center=(self.config.screen_width // 2, 30))
        self.screen.blit(text, text_rect)

    def _render_simulation(self) -> None:
        """Render the simulated star."""
        if not self.screen or not self.star_position:
            return

        # Draw the star as a bright circle
        star_color = (
            self.config.star_brightness,
            self.config.star_brightness,
            self.config.star_brightness,
        )
        pygame.draw.circle(
            self.screen,
            star_color,
            (int(self.star_position.x), int(self.star_position.y)),
            self.config.star_size,
        )

    def quit(self) -> None:
        """Cleanup and quit pygame."""
        self.running = False
        pygame.quit()
