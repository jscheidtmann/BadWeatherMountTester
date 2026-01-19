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
from typing import Optional, Tuple, List

from badweathermounttester.config import DisplayConfig


class DisplayMode(Enum):
    """Current display mode."""

    WAITING = auto()
    LOCATOR = auto()
    ALIGN = auto()  # Horizontal lines for alignment
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
        # Calibration state
        self.calibration_hover_position: Optional[Tuple[int, int]] = None
        self.calibration_points: List[Tuple[int, int]] = []
        self.calibration_selected_index: int = -1  # -1 means no selection
        self.calibration_polynomial: Optional[List[float]] = None  # Coefficients [a, b, c, d] for ax³+bx²+cx+d

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

    def set_calibration_hover(self, x: int, y: int) -> None:
        """Set the calibration hover crosshair position."""
        self.calibration_hover_position = (x, y)

    def set_calibration_points(self, points: List[Tuple[int, int]]) -> None:
        """Set all calibration points."""
        self.calibration_points = list(points)

    def add_calibration_point(self, x: int, y: int) -> None:
        """Add a single calibration point."""
        self.calibration_points.append((x, y))

    def clear_calibration_points(self) -> None:
        """Clear all calibration points."""
        self.calibration_points = []
        self.calibration_hover_position = None
        self.calibration_selected_index = -1
        self.calibration_polynomial = None

    def set_calibration_selected_index(self, index: int) -> None:
        """Set the selected calibration point index."""
        self.calibration_selected_index = index

    def set_calibration_polynomial(self, coeffs: Optional[List[float]]) -> None:
        """Set the polynomial coefficients for the fitted curve."""
        self.calibration_polynomial = coeffs

    def update_calibration_point(self, index: int, x: int, y: int) -> None:
        """Update a specific calibration point's position."""
        if 0 <= index < len(self.calibration_points):
            self.calibration_points[index] = (x, y)

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
        elif self.mode == DisplayMode.ALIGN:
            self._render_align()
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

    def _draw_grid(self, parts: int = 4, color: Tuple[int, int, int] = (0, 0, 255)) -> None:
        """Draw a grid on the screen."""
        if not self.screen:
            return

        width = self.config.screen_width
        height = self.config.screen_height

        spacing_w = width // parts
        spacing_h = height // parts
        for x in range(0, width, spacing_w):
            pygame.draw.line(self.screen, color, (x, 0), (x, height), 1)
        for y in range(0, height, spacing_h):
            pygame.draw.line(self.screen, color, (0, y), (width, y), 1)
       
        # Draw lines at the right and bottom edges
        pygame.draw.line(self.screen, color, (width - 1, 0), (width - 1, height), 1)
        pygame.draw.line(self.screen, color, (0, height - 1), (width, height - 1), 1)

    def _render_locator(self) -> None:
        """Render the locator screen with arrows pointing to target."""
        if not self.screen:
            return

        self._draw_grid()

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

    def _render_align(self) -> None:
        """Render horizontal lines for alignment. Line at crosshair position is red."""
        if not self.screen:
            return

        width = self.config.screen_width
        height = self.config.screen_height
        line_spacing = 50
        gray_color = (128, 128, 128)  # 50% gray
        red_color = (255, 0, 0)

        # Use the same target position as the locator crosshair (1/3 from bottom = 2/3 from top)
        target_y = int(height * 2 / 3)

        font = pygame.font.Font(None, 24)

        # Draw horizontal lines 50px apart, centered on the target_y position
        # Lines above the target
        y = target_y
        while y >= 0:
            distance = target_y - y
            color = red_color if y == target_y else gray_color
            pygame.draw.line(self.screen, color, (0, y), (width, y), 1)

            # Draw distance labels at both ends
            label = font.render(str(distance), True, color)
            # Left side
            self.screen.blit(label, (5, y - label.get_height() - 2))
            # Right side
            self.screen.blit(label, (width - label.get_width() - 5, y - label.get_height() - 2))

            y -= line_spacing

        # Lines below the target (negative distances)
        y = target_y + line_spacing
        while y <= height:
            distance = target_y - y  # Negative for lines below
            pygame.draw.line(self.screen, gray_color, (0, y), (width, y), 1)

            # Draw distance labels at both ends
            label = font.render(str(distance), True, gray_color)
            # Left side
            self.screen.blit(label, (5, y - label.get_height() - 2))
            # Right side
            self.screen.blit(label, (width - label.get_width() - 5, y - label.get_height() - 2))

            y += line_spacing

    def _render_calibration(self) -> None:
        """Render the calibration screen with hover crosshair and collected points."""
        if not self.screen:
            return

        # Draw grid background
        self._draw_grid()

        width = self.config.screen_width
        height = self.config.screen_height

        # Colors
        point_color = (0, 255, 0)  # Green for recorded points
        selected_color = (255, 255, 0)  # Yellow for selected point
        line_color = (255, 165, 0)  # Orange for connecting line
        hover_color = (255, 255, 255)  # White for hover crosshair
        poly_color = (255, 0, 0)  # Red for polynomial fit

        # Draw polynomial fit curve if available
        if self.calibration_polynomial and len(self.calibration_points) > 3:
            a, b, c, d = self.calibration_polynomial
            # Get x range from points
            x_coords = [p[0] for p in self.calibration_points]
            x_min, x_max = min(x_coords), max(x_coords)
            # Draw curve by connecting many points
            poly_points = []
            for x in range(x_min, x_max + 1, 2):  # Step by 2 pixels for performance
                y = a * x**3 + b * x**2 + c * x + d
                if 0 <= y <= height:
                    poly_points.append((x, int(y)))
            if len(poly_points) > 1:
                pygame.draw.lines(self.screen, poly_color, False, poly_points, 2)

        # Draw connecting line between calibration points
        if len(self.calibration_points) > 1:
            pygame.draw.lines(self.screen, line_color, False, self.calibration_points, 2)

        # Draw calibration points as crosshairs
        for i, (px, py) in enumerate(self.calibration_points):
            is_selected = (i == self.calibration_selected_index)
            color = selected_color if is_selected else point_color
            size = 12 if is_selected else 8
            self._draw_crosshair(px, py, size=size, color=color)
            # Draw point number
            font = pygame.font.Font(None, 20)
            label = font.render(str(i + 1), True, color)
            self.screen.blit(label, (px + 10, py - 10))

        # Draw hover crosshair (larger than point markers)
        if self.calibration_hover_position:
            hx, hy = self.calibration_hover_position
            self._draw_crosshair(hx, hy, size=15, color=hover_color)

        # Display point count and instructions
        font = pygame.font.Font(None, 36)
        text = font.render(f"Calibration - Points: {len(self.calibration_points)}", True, (255, 255, 0))
        text_rect = text.get_rect(center=(width // 2, 30))
        self.screen.blit(text, text_rect)

        # Instructions at bottom
        font_small = pygame.font.Font(None, 28)
        instr = font_small.render("Move mouse on web UI to position crosshair, click to record point", True, (200, 200, 200))
        instr_rect = instr.get_rect(center=(width // 2, height - 30))
        self.screen.blit(instr, instr_rect)

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
