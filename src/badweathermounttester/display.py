"""Display/Simulator component for Bad Weather Mount Tester.

This module handles the pygame-based display that shows:
- The BWMT logo and waiting screen
- The locator screen for finding the screen with the guide scope
- The simulated star for guiding
"""

import math
import time
from pathlib import Path

import numpy as np
import pygame
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

from badweathermounttester.config import DisplayConfig

# Path to the logo file
LOGO_PATH = Path(__file__).parent / "static" / "BWMT_logo_w.png"


def generate_beep_sound(
    frequency: int = 880, duration_ms: int = 150, sample_rate: int = 44100, volume: float = 0.3
) -> pygame.mixer.Sound:
    """Generate a beep sound as a sine wave.

    Args:
        frequency: Frequency in Hz (default 880 = A5)
        duration_ms: Duration in milliseconds
        sample_rate: Audio sample rate
        volume: Volume from 0.0 to 1.0

    Returns:
        pygame.mixer.Sound object
    """
    num_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, num_samples, dtype=np.float32)

    # Generate sine wave with fade in/out to avoid clicks
    wave = np.sin(2 * np.pi * frequency * t)

    # Apply envelope (fade in/out over 10ms)
    fade_samples = int(sample_rate * 0.01)
    if fade_samples > 0 and num_samples > 2 * fade_samples:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        wave[:fade_samples] *= fade_in
        wave[-fade_samples:] *= fade_out

    # Scale to 16-bit integer range and apply volume
    wave = (wave * volume * 32767).astype(np.int16)

    # Create stereo by duplicating the channel
    stereo_wave = np.column_stack((wave, wave))

    return pygame.mixer.Sound(buffer=stereo_wave)


class DisplayMode(Enum):
    """Current display mode."""

    WAITING = auto()
    LOCATOR = auto()
    ALIGN = auto()  # Horizontal lines for alignment
    CALIBRATION = auto()
    VELOCITY_MEASURE = auto()  # Velocity measurement with vertical stripes
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
        self.calibration_ellipse: Optional[Dict] = None  # Ellipse parameters dict
        # Simulation state
        self.simulation_running: bool = False
        self.simulation_start_time: Optional[float] = None
        self.simulation_elapsed: float = 0.0  # Elapsed time in seconds (stored when paused)
        self.simulation_x_start: int = 0
        self.simulation_x_end: int = 0
        self.simulation_pixels_per_second: float = 1.0  # Will be calculated from sidereal rate
        # Variable velocity lookup tables (for interpolated measured velocities)
        self.simulation_lookup_xs: Optional[np.ndarray] = None
        self.simulation_lookup_ts: Optional[np.ndarray] = None
        self.simulation_lookup_vs: Optional[np.ndarray] = None
        self.simulation_total_time: float = 0.0
        # duration of each simulation step in seconds
        self.simu_render: Optional[float] = None
        # Audio/beep state
        self.beep_sound: Optional[pygame.mixer.Sound] = None
        self.beep_end_sound: Optional[pygame.mixer.Sound] = None  # Lower, longer beep for end
        self.beep_60s_triggered: bool = False
        self.beep_30s_triggered: bool = False
        self.countdown_last_second: int = -1  # Track last countdown second beeped
        self.beep_end_triggered: bool = False  # Track if end beep was played
        # Logo surface (loaded in init)
        self.logo: Optional[pygame.Surface] = None
        # Velocity measurement state
        self.velocity_stripe_width: int = 0  # Width of each stripe in pixels
        self.velocity_pixels_per_second: float = 0.0  # Calculated velocity

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
            self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height))

        self.clock = pygame.time.Clock()
        self.running = True

        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

        # Load logo
        self._load_logo()

        # Initialize audio system and generate beep sound
        self._init_audio()

    def _load_logo(self) -> None:
        """Load the BWMT logo image."""
        try:
            if LOGO_PATH.exists():
                self.logo = pygame.image.load(str(LOGO_PATH)).convert_alpha()
            else:
                print(f"Warning: Logo file not found: {LOGO_PATH}")
        except pygame.error as e:
            print(f"Warning: Could not load logo: {e}")

    def _init_audio(self) -> None:
        """Initialize the audio system and play startup beep to test audio."""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.beep_sound = generate_beep_sound(frequency=880, duration_ms=150, volume=0.3)
            # Lower (440 Hz = A4) and longer (500ms) beep for simulation end
            self.beep_end_sound = generate_beep_sound(frequency=440, duration_ms=500, volume=0.3)
            # Play startup beep to verify audio is working
            self.beep_sound.play()
        except pygame.error as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.beep_sound = None
            self.beep_end_sound = None

    def play_beep(self) -> None:
        """Play a beep sound if audio is available."""
        if self.beep_sound:
            self.beep_sound.play()

    def reset_beep_state(self) -> None:
        """Reset beep tracking state. Call when simulation is reset."""
        self.beep_60s_triggered = False
        self.beep_30s_triggered = False
        self.countdown_last_second = -1
        self.beep_end_triggered = False

    def _check_and_play_beeps(self, remaining_seconds: float, complete: bool) -> None:
        """Check timing thresholds and play beeps as needed.

        Beeps at:
        - 60 seconds remaining (once)
        - 30 seconds remaining (once)
        - 10 down to 1 second (countdown, one beep per second)
        - Simulation complete (lower, longer beep)
        """
        if self.beep_sound is None:
            return

        # End beep - lower and longer when simulation completes
        if complete and not self.beep_end_triggered and self.beep_end_sound:
            self.beep_end_sound.play()
            self.beep_end_triggered = True
            return

        if not self.simulation_running:
            return

        # 60 second warning
        if not self.beep_60s_triggered and remaining_seconds <= 60.0 and remaining_seconds > 59.0:
            self.play_beep()
            self.beep_60s_triggered = True

        # 30 second warning
        if not self.beep_30s_triggered and remaining_seconds <= 30.0 and remaining_seconds > 29.0:
            self.play_beep()
            self.beep_30s_triggered = True

        # Countdown from 10 to 1
        if remaining_seconds <= 10.0 and remaining_seconds > 0:
            current_second = int(remaining_seconds)
            # Beep when we cross into a new second (10, 9, 8, ... 1)
            if current_second != self.countdown_last_second and current_second >= 1:
                self.play_beep()
                self.countdown_last_second = current_second

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
        """Set all calibration points, sorted by x coordinate."""
        self.calibration_points = sorted(points, key=lambda p: p[0])

    def add_calibration_point(self, x: int, y: int) -> int:
        """Add a single calibration point and sort by x coordinate.

        Returns the index of the newly added point after sorting.
        """
        self.calibration_points.append((x, y))
        self.calibration_points.sort(key=lambda p: p[0])
        # Find the index of the newly added point
        return next(i for i, p in enumerate(self.calibration_points) if p == (x, y))

    def clear_calibration_points(self) -> None:
        """Clear all calibration points."""
        self.calibration_points = []
        self.calibration_hover_position = None
        self.calibration_selected_index = -1
        self.calibration_ellipse = None

    def set_calibration_selected_index(self, index: int) -> None:
        """Set the selected calibration point index."""
        self.calibration_selected_index = index

    def set_calibration_ellipse(self, ellipse: Optional[Dict]) -> None:
        """Set the ellipse parameters for the fitted curve."""
        self.calibration_ellipse = ellipse

    def update_calibration_point(self, index: int, x: int, y: int) -> None:
        """Update a specific calibration point's position."""
        if 0 <= index < len(self.calibration_points):
            self.calibration_points[index] = (x, y)

    def setup_simulation(
        self,
        x_start: int,
        x_end: int,
        pixels_per_second: float,
        velocity_profile: Optional[List[Tuple[float, float]]] = None,
    ) -> None:
        """Set up simulation parameters.

        Args:
            x_start: Starting x position in pixels
            x_end: Ending x position in pixels
            pixels_per_second: Constant velocity (used as fallback or when no profile)
            velocity_profile: Optional list of (x_center, velocity) tuples for variable speed.
                            When provided, a quadratic polynomial is fit and used to create
                            a lookup table mapping x-positions to cumulative elapsed times.
        """
        self.simulation_x_start = x_start
        self.simulation_x_end = x_end
        self.simulation_pixels_per_second = pixels_per_second
        self.simulation_running = False
        self.simulation_start_time = None
        self.simulation_elapsed = 0.0
        self.reset_beep_state()

        if velocity_profile is not None and len(velocity_profile) >= 3:
            # Fit quadratic polynomial through measured velocity points
            profile_xs = np.array([p[0] for p in velocity_profile])
            profile_vs = np.array([p[1] for p in velocity_profile])
            coeffs = np.polyfit(profile_xs, profile_vs, 2)

            # Create dense x grid from x_start to x_end
            lookup_xs = np.linspace(float(x_start), float(x_end), 1000)
            # Evaluate velocity at each x, clamp to minimum 0.01 px/s
            lookup_vs = np.maximum(np.polyval(coeffs, lookup_xs), 0.01)

            # Compute cumulative time: dt[i] = dx / avg_velocity between points
            dx = np.diff(lookup_xs)
            avg_vs = (lookup_vs[:-1] + lookup_vs[1:]) / 2.0
            dt = dx / avg_vs
            lookup_ts = np.concatenate(([0.0], np.cumsum(dt)))

            self.simulation_lookup_xs = lookup_xs
            self.simulation_lookup_ts = lookup_ts
            self.simulation_lookup_vs = lookup_vs
            self.simulation_total_time = float(lookup_ts[-1])
        else:
            self.simulation_lookup_xs = None
            self.simulation_lookup_ts = None
            self.simulation_lookup_vs = None
            self.simulation_total_time = 0.0

    def start_simulation(self) -> None:
        """Start or resume the simulation."""
        if not self.simulation_running:
            self.simulation_running = True
            # Set start_time so that elapsed calculation gives correct value
            # start_time = now - already_elapsed
            self.simulation_start_time = time.time() - self.simulation_elapsed

    def stop_simulation(self) -> None:
        """Stop/pause the simulation."""
        if self.simulation_running and self.simulation_start_time is not None:
            # Store the elapsed time before pausing
            self.simulation_elapsed = time.time() - self.simulation_start_time
        self.simulation_running = False

    def reset_simulation(self) -> None:
        """Reset the simulation to the start."""
        self.simulation_running = False
        self.simulation_start_time = None
        self.simulation_elapsed = 0.0
        self.reset_beep_state()

    def _get_total_time(self) -> float:
        """Get the total simulation time in seconds."""
        if self.simulation_lookup_ts is not None:
            return self.simulation_total_time
        total_distance = self.simulation_x_end - self.simulation_x_start
        return total_distance / self.simulation_pixels_per_second if self.simulation_pixels_per_second > 0 else 0

    def _x_from_elapsed(self, elapsed: float) -> float:
        """Get the x position from elapsed time."""
        if self.simulation_lookup_ts is not None and self.simulation_lookup_xs is not None:
            return float(np.interp(elapsed, self.simulation_lookup_ts, self.simulation_lookup_xs))
        return self.simulation_x_start + elapsed * self.simulation_pixels_per_second

    def _velocity_from_elapsed(self, elapsed: float) -> float:
        """Get the instantaneous velocity (px/s) at the given elapsed time."""
        if (
            self.simulation_lookup_ts is not None
            and self.simulation_lookup_xs is not None
            and self.simulation_lookup_vs is not None
        ):
            return float(np.interp(elapsed, self.simulation_lookup_ts, self.simulation_lookup_vs))
        return self.simulation_pixels_per_second

    def skip_simulation(self, seconds: float) -> None:
        """Skip the simulation forward or backward by the given number of seconds."""
        total_time = self._get_total_time()

        if self.simulation_running and self.simulation_start_time is not None:
            # Currently running - adjust start time
            self.simulation_start_time -= seconds
            # Clamp
            elapsed = time.time() - self.simulation_start_time
            if elapsed < 0:
                self.simulation_start_time = time.time()
            elif elapsed > total_time:
                self.simulation_start_time = time.time() - total_time
        else:
            # Paused - adjust stored elapsed time
            self.simulation_elapsed += seconds
            # Clamp
            if self.simulation_elapsed < 0:
                self.simulation_elapsed = 0.0
            elif self.simulation_elapsed > total_time:
                self.simulation_elapsed = total_time

    def seek_simulation(self, elapsed_seconds: float) -> None:
        """Seek the simulation to a specific elapsed time."""
        total_time = self._get_total_time()

        # Clamp to valid range
        elapsed_seconds = max(0.0, min(elapsed_seconds, total_time))

        if self.simulation_running and self.simulation_start_time is not None:
            # Currently running - adjust start time so elapsed calculation is correct
            self.simulation_start_time = time.time() - elapsed_seconds
        else:
            # Paused - set stored elapsed time directly
            self.simulation_elapsed = elapsed_seconds

    def setup_velocity_measurement(self, pixels_per_second: float) -> None:
        """Set up velocity measurement display with calculated stripe width.

        Args:
            pixels_per_second: The calculated sidereal velocity in pixels/second
        """
        self.velocity_pixels_per_second = pixels_per_second
        # Calculate stripe width for ~3 minutes (180 seconds) crossing time
        self.velocity_stripe_width = int(pixels_per_second * 180)
        # Ensure minimum width of 50 pixels
        if self.velocity_stripe_width < 50:
            self.velocity_stripe_width = 50

    def get_velocity_stripe_width(self) -> int:
        """Get the current velocity stripe width."""
        return self.velocity_stripe_width

    def _ellipse_y_from_x(self, x: float, use_upper_arc: Optional[bool] = None) -> Optional[float]:
        """Calculate y coordinate on ellipse for given x using the conic equation.

        The ellipse is defined by: Ax² + Bxy + Cy² + Dx + Ey + F = 0
        Solving for y: Cy² + (Bx + E)y + (Ax² + Dx + F) = 0

        Args:
            x: The x coordinate
            use_upper_arc: If True, use upper arc (smaller y). If False, use lower arc.
                          If None, determine from calibration points.
        """
        if not self.calibration_ellipse or "coeffs" not in self.calibration_ellipse:
            return None

        A, B, C, D, E, F = self.calibration_ellipse["coeffs"]
        center_y = self.calibration_ellipse.get("center_y", 0)

        # Quadratic coefficients for y
        qa = C
        qb = B * x + E
        qc = A * x * x + D * x + F

        discriminant = qb * qb - 4 * qa * qc

        if discriminant < 0 or abs(qa) < 1e-10:
            return None

        sqrt_disc = math.sqrt(discriminant)
        y1 = (-qb + sqrt_disc) / (2 * qa)
        y2 = (-qb - sqrt_disc) / (2 * qa)

        # Determine which arc to use based on calibration points
        if use_upper_arc is None:
            # Check if calibration points are mostly above or below center
            if self.calibration_points:
                points_above = sum(1 for p in self.calibration_points if p[1] < center_y)
                use_upper_arc = points_above > len(self.calibration_points) / 2
            else:
                use_upper_arc = True

        # Pick the appropriate arc consistently
        if use_upper_arc:
            return min(y1, y2)  # Upper arc = smaller y value
        else:
            return max(y1, y2)  # Lower arc = larger y value

    def get_simulation_status(self) -> dict:
        """Get current simulation status."""
        if not self.calibration_ellipse or self.simulation_x_start >= self.simulation_x_end:
            return {
                "running": False,
                "progress": 0,
                "elapsed_seconds": 0,
                "remaining_seconds": 0,
                "current_x": self.simulation_x_start,
                "current_y": 0,
                "complete": False,
            }

        total_distance = self.simulation_x_end - self.simulation_x_start
        total_time = self._get_total_time()

        # Get elapsed time: from start_time if running, from stored elapsed if paused
        if self.simulation_running and self.simulation_start_time is not None:
            elapsed = time.time() - self.simulation_start_time
        else:
            elapsed = self.simulation_elapsed

        current_x = self._x_from_elapsed(elapsed)
        current_x = min(current_x, float(self.simulation_x_end))

        # Calculate y from ellipse
        y = self._ellipse_y_from_x(current_x)
        current_y = y if y is not None else self.calibration_ellipse.get("center_y", 0)

        current_velocity = self._velocity_from_elapsed(elapsed)

        progress = (current_x - self.simulation_x_start) / total_distance * 100 if total_distance > 0 else 100
        remaining = max(0, total_time - elapsed)
        complete = bool(current_x >= self.simulation_x_end)

        if complete:
            self.simulation_running = False
            self.simulation_elapsed = total_time  # Store final elapsed time

        return {
            "running": self.simulation_running,
            "progress": round(progress, 1),
            "elapsed_seconds": round(elapsed, 1),
            "remaining_seconds": round(remaining, 1),
            "total_seconds": round(total_time, 1),
            "current_x": current_x,
            "current_y": current_y,
            "current_velocity": round(current_velocity, 4),
            "complete": complete,
        }

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
        elif self.mode == DisplayMode.VELOCITY_MEASURE:
            self._render_velocity_measure()
        elif self.mode == DisplayMode.SIMULATION:
            self._render_simulation()

        pygame.display.flip()

    def _render_waiting(self) -> None:
        """Render the waiting screen with logo and network address."""
        if not self.screen:
            return

        # Scale font sizes based on screen height
        font_small = pygame.font.Font(None, max(20, int(self.config.screen_height * 0.03)))

        # Title - dynamically sized to span screen width
        title_text = "Bad Weather Mount Tester"
        margin = int(self.config.screen_width * 0.02)  # 2% margin on each side
        target_width = self.config.screen_width - 2 * margin

        # Start with a base font size and calculate the needed size
        base_size = max(36, int(self.config.screen_height * 0.067))
        base_font = pygame.font.Font(None, base_size)
        base_title = base_font.render(title_text, True, (255, 255, 255))
        base_width = base_title.get_width()

        # Scale font size proportionally to fill screen width
        title_font_size = int(base_size * target_width / base_width)
        font_large = pygame.font.Font(None, title_font_size)
        title = font_large.render(title_text, True, (255, 255, 255))
        title_y = int(self.config.screen_height * 0.1)  # 10% from top
        title_rect = title.get_rect(center=(self.config.screen_width // 2, title_y))
        self.screen.blit(title, title_rect)

        # Logo - centered on screen
        if self.logo:
            # Scale logo to fit nicely (max 80% of screen width, maintain aspect ratio)
            max_logo_width = int(self.config.screen_width * 0.8)
            max_logo_height = int(self.config.screen_height * 0.4)
            logo_width, logo_height = self.logo.get_size()

            scale = min(max_logo_width / logo_width, max_logo_height / logo_height)
            new_width = int(logo_width * scale)
            new_height = int(logo_height * scale)

            scaled_logo = pygame.transform.smoothscale(self.logo, (new_width, new_height))
            logo_rect = scaled_logo.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2))
            self.screen.blit(scaled_logo, logo_rect)

        # Instructions at bottom
        instructions = font_small.render("Press ESC to exit", True, (150, 150, 150))
        instr_y = self.config.screen_height - int(self.config.screen_height * 0.05)  # 5% from bottom
        instr_rect = instructions.get_rect(center=(self.config.screen_width // 2, instr_y))
        self.screen.blit(instructions, instr_rect)

        # Network address - just above instructions, dynamically sized to fit screen
        if self.network_address:
            connect_text = f"Connect to: {self.network_address}"
            # Start with a base font size and calculate the needed size
            connect_base_size = max(36, int(min(self.config.screen_height, self.config.screen_width) * 0.11))
            connect_base_font = pygame.font.Font(None, connect_base_size)
            connect_base = connect_base_font.render(connect_text, True, (100, 255, 100))
            connect_base_width = connect_base.get_width()

            # If text is too wide, scale it down to fit
            if connect_base_width > target_width:
                connect_font_size = int(connect_base_size * target_width / connect_base_width)
                font_connect = pygame.font.Font(None, connect_font_size)
            else:
                font_connect = connect_base_font

            addr_text = font_connect.render(connect_text, True, (100, 255, 100))
            addr_y = self.config.screen_height - int(self.config.screen_height * 0.18)  # 18% from bottom
            addr_rect = addr_text.get_rect(center=(self.config.screen_width // 2, addr_y))
            self.screen.blit(addr_text, addr_rect)

    def _draw_arrow(
        self,
        x: int,
        y: int,
        target_x: int,
        target_y: int,
        size: int = 10,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
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

        # Target: leftmost column, at configured vertical ratio
        target_x = 10
        target_y = int(height * self.config.target_y_ratio)

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

        # Use the same target position as the locator crosshair
        target_y = int(height * self.config.target_y_ratio)

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

        # Colors - grayscale for B/W camera compatibility
        point_color = (160, 160, 160)  # Medium gray for recorded points
        selected_color = (255, 255, 255)  # Bright white for selected point
        line_color = (80, 80, 80)  # Dim gray for connecting line
        hover_color = (255, 255, 255)  # White for hover crosshair

        # Draw connecting line between calibration points
        if len(self.calibration_points) > 1:
            pygame.draw.lines(self.screen, line_color, False, self.calibration_points, 2)

        # Draw calibration points as crosshairs
        for i, (px, py) in enumerate(self.calibration_points):
            is_selected = i == self.calibration_selected_index
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
        text = font.render(f"Calibration - Points: {len(self.calibration_points)}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(width // 2, 30))
        self.screen.blit(text, text_rect)

        # Instructions at bottom
        font_small = pygame.font.Font(None, 28)
        instr = font_small.render(
            "Move mouse on web UI to position crosshair, click to record point", True, (200, 200, 200)
        )
        instr_rect = instr.get_rect(center=(width // 2, height - 30))
        self.screen.blit(instr, instr_rect)

    def _render_velocity_measure(self) -> None:
        """Render the velocity measurement screen with three vertical stripes."""
        if not self.screen:
            return

        width = self.config.screen_width
        height = self.config.screen_height

        # Draw the fitted ellipse trace from calibration as reference (dim)
        if self.calibration_ellipse and "coeffs" in self.calibration_ellipse:
            A, B, C, D, E, F = self.calibration_ellipse["coeffs"]
            center_y = self.calibration_ellipse.get("center_y", 0)

            # Determine which arc to use based on calibration points
            if self.calibration_points:
                points_above = sum(1 for p in self.calibration_points if p[1] < center_y)
                use_upper_arc = points_above > len(self.calibration_points) / 2
            else:
                use_upper_arc = True

            # Draw ellipse trace (dim gray)
            pygame.draw.aaline  # for smoother line
            prev_point = None
            for x in range(0, width, 2):
                qa = C
                qb = B * x + E
                qc = A * x * x + D * x + F
                discriminant = qb * qb - 4 * qa * qc

                if discriminant >= 0 and abs(qa) > 1e-10:
                    sqrt_disc = math.sqrt(discriminant)
                    y1 = (-qb + sqrt_disc) / (2 * qa)
                    y2 = (-qb - sqrt_disc) / (2 * qa)
                    y = min(y1, y2) if use_upper_arc else max(y1, y2)

                    if 0 <= y <= height:
                        current_point = (int(x), int(y))
                        if prev_point:
                            pygame.draw.line(self.screen, (40, 40, 40), prev_point, current_point, 1)
                        prev_point = current_point
                else:
                    prev_point = None

        stripe_width = int(self.velocity_stripe_width)
        if stripe_width < 50:
            stripe_width = 50  # Minimum visible width

        # Calculate stripe left edges: flush left, centered, flush right
        stripe_left_edges = [
            0,  # Left stripe flush with left edge
            (width - stripe_width) // 2,  # Middle stripe centered
            width - stripe_width,  # Right stripe flush with right edge
        ]
        stripe_base_labels = ["LEFT ", "MIDDLE ", "RIGHT "]

        # Stripe color (gray for B/W camera)
        stripe_color = (200, 200, 200)

        # Small font for labels, so it can be read in guidescope image
        font_small = pygame.font.Font(None, 12)

        for i, (left_edge, base_label) in enumerate(zip(stripe_left_edges, stripe_base_labels)):
            # Draw vertical stripe
            rect = pygame.Rect(left_edge, 0, stripe_width, height)
            pygame.draw.rect(self.screen, stripe_color, rect)

            # Calculate how many repetitions needed to fill screen height
            # Render single label to measure its width (becomes height when rotated)
            single_surface = font_small.render(base_label, True, stripe_color)
            single_width = single_surface.get_width()
            # Calculate repetitions needed to fill height, add 1 to ensure full coverage
            repetitions = (height // single_width) + 1
            label = base_label * repetitions

            # Draw label next to stripe, rotated to read bottom-to-top
            # 10 pixel gap between stripe and text
            label_surface = font_small.render(label, True, stripe_color)
            # Rotate 90 degrees counter-clockwise (text reads bottom to top)
            rotated_label = pygame.transform.rotate(label_surface, 90)

            if i == 0:  # LEFT stripe - label to the right of stripe
                label_x = left_edge + stripe_width + 10
                label_rect = rotated_label.get_rect(left=label_x, bottom=height)
            elif i == 2:  # RIGHT stripe - label to the left of stripe
                label_x = left_edge - 10 - rotated_label.get_width()
                label_rect = rotated_label.get_rect(left=label_x, bottom=height)
            else:  # MIDDLE stripe - label to the right of stripe
                label_x = left_edge + stripe_width + 10
                label_rect = rotated_label.get_rect(left=label_x, bottom=height)
            self.screen.blit(rotated_label, label_rect)

    def _render_simulation(self) -> None:
        """Render the simulated star moving along the ellipse curve."""
        if not self.screen:
            return

        width = self.config.screen_width
        height = self.config.screen_height

        # Get current simulation status
        status = self.get_simulation_status()
        current_x = status["current_x"]
        current_y = status["current_y"]

        # Check timing and play warning beeps
        self._check_and_play_beeps(status["remaining_seconds"], status["complete"])

        start = time.time()
        # Draw the star as a 2D Gaussian distribution with subpixel accuracy
        # sigma = FWHM / (2 * sqrt(2 * ln(2))) ≈ FWHM / 2.355
        if self.calibration_ellipse and 0 <= current_y <= height:
            fwhm = self.config.star_size
            sigma = fwhm / 2.355
            max_brightness = self.config.star_brightness

            # Draw pixels in a region around the star (3*sigma is enough to capture most of the light)
            radius = int(3 * sigma) + 1
            # Calculate the bounding box of pixels to render
            px_min = int(current_x) - radius
            px_max = int(current_x) + radius + 1
            py_min = int(current_y) - radius
            py_max = int(current_y) + radius + 1

            for py in range(py_min, py_max + 1):
                for px in range(px_min, px_max + 1):
                    # Skip if outside screen
                    if px < 0 or px >= width or py < 0 or py >= height:
                        continue

                    # Calculate distance from pixel center to star position (subpixel accuracy)
                    dist_x = px - current_x
                    dist_y = py - current_y
                    dist_sq = dist_x * dist_x + dist_y * dist_y
                    brightness = max_brightness * math.exp(-dist_sq / (2 * sigma * sigma))

                    if brightness >= 1:  # Only draw if brightness is visible
                        gray = int(brightness)
                        self.screen.set_at((px, py), (gray, gray, gray))
        end = time.time()
        self.simu_render = end - start

        # Draw status info at top - large font for visibility from distance
        font_status = pygame.font.Font(None, 72)
        font_time = pygame.font.Font(None, 200)  # Very large for time remaining
        if status["complete"]:
            text = font_status.render("Simulation Complete", True, (0, 255, 0))
            text_rect = text.get_rect(center=(width // 2, 50))
            self.screen.blit(text, text_rect)
        elif status["running"]:
            remaining = status["remaining_seconds"]
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            # Draw "Running" label
            label = font_status.render("Running", True, (255, 255, 0))
            label_rect = label.get_rect(center=(width // 2, 40))
            self.screen.blit(label, label_rect)
            # Draw large time remaining
            time_text = font_time.render(f"{mins:02d}:{secs:02d}", True, (255, 255, 0))
            time_rect = time_text.get_rect(center=(width // 2, 130))
            self.screen.blit(time_text, time_rect)
        else:
            text = font_status.render("Simulation Ready - Press Start", True, (200, 200, 200))
            text_rect = text.get_rect(center=(width // 2, 50))
            self.screen.blit(text, text_rect)

        font_small = pygame.font.Font(None, 24)
        # Draw FPS in top-right corner
        if self.clock:
            fps = self.clock.get_fps()
            fps_text = font_small.render(f"{fps:.1f} fps ({self.simu_render:.3f}s)", True, (200, 200, 200))
            fps_rect = fps_text.get_rect(topright=(width - 10, 10))
            self.screen.blit(fps_text, fps_rect)

    def quit(self) -> None:
        """Cleanup and quit pygame."""
        self.running = False
        pygame.quit()
