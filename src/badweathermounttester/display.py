"""Display/Simulator component for Bad Weather Mount Tester.

This module handles the pygame-based display that shows:
- The BWMT logo and waiting screen
- The locator screen for finding the screen with the guide scope
- The simulated star for guiding
"""

import math

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

    def _draw_arrow(self, x: int, y: int, target_x: int, target_y: int,
                     size: int = 10, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Draw a small arrow at (x, y) pointing toward (target_x, target_y)."""
        if not self.screen:
            return

        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            return

        # Normalize direction
        dx /= dist
        dy /= dist

        # Arrow tip is at (x, y), base is behind it
        tip_x = x + dx * (size // 2)
        tip_y = y + dy * (size // 2)
        base_x = x - dx * (size // 2)
        base_y = y - dy * (size // 2)

        # Perpendicular for arrow wings
        perp_x = -dy
        perp_y = dx
        wing_size = size // 3

        # Draw arrow line
        pygame.draw.line(self.screen, color, (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), 1)

        # Draw arrow head wings
        wing1_x = tip_x - dx * wing_size + perp_x * wing_size
        wing1_y = tip_y - dy * wing_size + perp_y * wing_size
        wing2_x = tip_x - dx * wing_size - perp_x * wing_size
        wing2_y = tip_y - dy * wing_size - perp_y * wing_size

        pygame.draw.line(self.screen, color, (int(tip_x), int(tip_y)), (int(wing1_x), int(wing1_y)), 1)
        pygame.draw.line(self.screen, color, (int(tip_x), int(tip_y)), (int(wing2_x), int(wing2_y)), 1)

    def _draw_crosshair(self, x: int, y: int, size: int = 5, color: Tuple[int, int, int] = (255, 0, 0)) -> None:
        """Draw a crosshair at (x, y). size if half-length of crosshair lines."""
        if not self.screen:
            return

        pygame.draw.line(
            self.screen,
            color,
            (x - size, y),
            (x + size, y),
            1,
        )
        pygame.draw.line(
            self.screen,
            color,
            (x, y - size),
            (x, y + size),
            1,
        )

    def _render_locator(self) -> None:
        """Render the locator screen with arrows pointing to target."""
        if not self.screen:
            return

        width = self.config.screen_width
        height = self.config.screen_height

        # Target: leftmost column, 1/3 from bottom (= 2/3 from top)
        target_x = 10
        target_y = int(height * 2 / 3)

        self._draw_crosshair(target_x, target_y)

        # Draw arrows on a 20px grid
        grid_spacing = 20
        arrow_size = 10
        arrow_color = (255, 255, 255)

        for x in range(grid_spacing, width, grid_spacing):
            for y in range(grid_spacing, height, grid_spacing):
                self._draw_arrow(x, y, target_x, target_y, arrow_size, arrow_color)

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
