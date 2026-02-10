import argparse
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import yaml
from mpl_toolkits.mplot3d import Axes3D


def load_config(config_file: str | None = None) -> dict:
    """Load configuration from setup.yml or specified file."""
    if config_file:
        config_path = Path(config_file)
    else:
        config_path = Path(__file__).parent.parent.parent / "setup.yml"
        if not config_path.exists():
            config_path = Path("setup.yml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def parse_args(config: dict, config_file: str | None = None) -> argparse.Namespace:
    """Parse command line arguments with defaults from config."""
    mount = config.get("mount", {})
    display = config.get("display", {})

    parser = argparse.ArgumentParser(
        prog="geometry",
        description="Visualize telescope mount geometry and rotation",
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=config_file,
        help="Path to configuration file (default: setup.yml)",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=mount.get("latitude", 51.0),
        help=f"Latitude in degrees (default from setup.yml: {mount.get('latitude', 51.0)})",
    )
    parser.add_argument(
        "-or",
        "--offsetRA",
        type=float,
        default=mount.get("telescope_offset_m", 0.27),
        help=f"Telescope offset from RA/rotation axis (default from setup.yml: {mount.get('telescope_offset_m', 0.27)})",
    )
    parser.add_argument(
        "-od",
        "--offsetDec",
        type=float,
        default=mount.get("telescope_offset_dec_m", -0.015),
        help=f"Telescope offset from Dec axis (default from setup.yml: {mount.get('telescope_offset_dec_m', -0.015)})",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=mount.get("angle_start_deg", 0.0),
        help=f"Start angle in degrees (default from setup.yml: {mount.get('angle_start_deg', 0.0)})",
    )
    parser.add_argument(
        "--stop",
        type=float,
        default=mount.get("angle_stop_deg", -10.0),
        help=f"Stop angle in degrees (default from setup.yml: {mount.get('angle_stop_deg', -10.0)})",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=float,
        default=-mount.get("distance_to_screen_m", 3.41),
        help=f"Distance from origin along the line (default from setup.yml: {mount.get('distance_to_screen_m', 3.41)}m)",
    )
    parser.add_argument(
        "--dec",
        type=float,
        default=mount.get("declination_deg"),
        help="Declination in degrees for line of sight calculation",
    )
    parser.add_argument(
        "--screen-width",
        type=float,
        default=display.get("screen_width_mm", 520.0) / 1000.0,
        help=f"Screen width (default from setup.yml: {display.get('screen_width_mm', 520.0)}m)",
    )
    parser.add_argument(
        "--screen-height",
        type=float,
        default=display.get("screen_height_mm", 293.0) / 1000.0,
        help=f"Screen height (default from setup.yml: {display.get('screen_height_mm', 325.0)}m)",
    )
    parser.add_argument(
        "--screen-width-px",
        type=int,
        default=display.get("screen_width", 1920),
        help=f"Screen width in pixels (default from setup.yml: {display.get('screen_width', 1920)})",
    )
    parser.add_argument(
        "--screen-width-mm",
        type=float,
        default=display.get("screen_width_mm", 520.0),
        help=f"Screen width in mm (default from setup.yml: {display.get('screen_width_mm', 520.0)})",
    )
    return parser.parse_args()


def set_axes_equal(ax):
    limits = np.array([
        ax.get_xlim3d(),
        ax.get_ylim3d(),
        ax.get_zlim3d(),
    ])
    centers = np.mean(limits, axis=1)
    radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))

    ax.set_xlim3d([centers[0] - radius, centers[0] + radius])
    ax.set_ylim3d([centers[1] - radius, centers[1] + radius])
    ax.set_zlim3d([centers[2] - radius, centers[2] + radius])


def rotate(v, axis, angle):
    # ensure unit vector
    if abs(np.linalg.norm(axis)-1.0) > 1e-3:
        axis = axis / np.linalg.norm(axis)

    v = np.array(v)

    return (v * math.cos(angle) +
            np.cross(axis, v) * math.sin(angle) +
            axis * np.dot(axis, v) * (1 - math.cos(angle)))


def main():
    ########
    # Preparations
    ########
    # First pass: parse just --config to determine which config file to load
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("-c", "--config", type=str, default=None)
    pre_args, _ = pre_parser.parse_known_args()

    # Load config from specified file or default
    config = load_config(pre_args.config)
    args = parse_args(config, pre_args.config)

    dec_str = f", Declination: {args.dec}°" if args.dec is not None else ""
    print(f"Latitude: {args.lat}°, Offset RA: {args.offsetRA}m, Offset Dec: {args.offsetDec}m, Start: {args.start}°, Stop: {args.stop}°{dec_str}")

    lat = math.radians(args.lat)
    dec = math.radians(args.dec) if args.dec is not None else None

    # Coordinate system: x in direction of observer, y in direction of screen, z up to the ceiling

    # Rotation Axis of the telescope (unit vector)
    rot_axis = np.array((0, math.cos(lat), -math.sin(lat)))

    # Telescope is affixed off-axis to mount
    #  - First component of offset vector is offset from RA-axis (in direction of observer)
    #  - Second component is offset from Dec axis, which is zero here (negative is in direction of floor)
    o = np.array((args.offsetRA, args.offsetDec, 0))

    # Line of sight direction
    # if lat+dec = 90°, pointing straight to the screen.
    d = np.array((0, 1, 0))
    if dec is not None:
        d = np.array((0, math.cos(math.radians(90)-lat+dec), math.sin(math.radians(90)-lat+dec)))

    # Parameter range for drawing each line (one directional only, starting at Dec axis position)
    r = args.distance
    t = np.linspace(0, r, 100)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot rotation axis for clarity
    axis_line = rot_axis[None, :] * np.linspace(-r, r, 2)[:, None]
    ax.plot(axis_line[:, 0], axis_line[:, 1], axis_line[:, 2],
            color='green', linewidth=2, label="Rotation axis")

    # Plot origin
    ax.scatter(0, 0, 0, color="black", label="Origin")

    # Plot position of telescope (center of gravity, if optimally balanced)
    for deg in range(0, 361, 5):
        angle = math.radians(deg)

        # Rotate offset and direction
        o_rot = rotate(o, rot_axis, angle)
        d_rot = rotate(d, rot_axis, angle)

        # Plot the rotated offset point
        ax.scatter(o_rot[0], o_rot[1], o_rot[2], color="red", s=10)

    # Plot line of sight for the range of angles specified
    start_angle = args.start
    stop_angle = args.stop
    for deg in np.linspace(start_angle, stop_angle, 100):
        angle = math.radians(deg)

        # Rotate offset and direction
        o_rot = rotate(o, rot_axis, angle)
        d_rot = rotate(d, rot_axis, angle)

        # Create points of rotated line
        points = o_rot - t[:, None] * d_rot

        # Plot the rotated offset point
        ax.scatter(o_rot[0], o_rot[1], o_rot[2], color="red", s=10)

        # Plot the rotated line
        ax.plot(points[:, 0], points[:, 1], points[:, 2], alpha=0.8)

    # Line of sight for middle angle direction
    mid_angle = math.radians((start_angle + stop_angle) / 2)
    o_mid = rotate(o, rot_axis, mid_angle)
    d_mid = rotate(d, rot_axis, mid_angle)

    distance = -args.distance
    # Rectangle center at distance 3.8 from origin along the line
    rect_center = o_mid + distance * d_mid

    # Find two perpendicular vectors to d_mid for the rectangle plane
    # Use cross product with z-axis to get first perpendicular
    perp1 = np.cross(d_mid, np.array((0.0, 0.0, 1.0)))
    perp1 = perp1 / np.linalg.norm(perp1)
    # Second perpendicular is cross of d_mid and perp1
    perp2 = np.cross(perp1, d_mid)
    perp2 = perp2 / np.linalg.norm(perp2)

    # Rectangle dimensions (from setup.yml or command-line overrides)
    width, height = args.screen_width, args.screen_height

    # Rectangle corners
    corners = [
        rect_center + (width / 2) * perp1 + (height / 2) * perp2,
        rect_center - (width / 2) * perp1 + (height / 2) * perp2,
        rect_center - (width / 2) * perp1 - (height / 2) * perp2,
        rect_center + (width / 2) * perp1 - (height / 2) * perp2,
        rect_center + (width / 2) * perp1 + (height / 2) * perp2,  # close the rectangle
    ]
    corners = np.array(corners)

    ax.plot(corners[:, 0], corners[:, 1], corners[:, 2], color='blue', linewidth=2, label="Screen")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()

    set_axes_equal(ax)
    ax.view_init(elev=10, azim=75)

    # Plot intersections in second figure
    fig2, (ax2, ax3, ax4) = plt.subplots(3, 1, figsize=(6, 10))

    # Calculate intersections of lines with the screen plane
    # Plane defined by: (P - rect_center) · d_mid = 0
    intersections_x = []
    intersections_y = []

    for deg in np.linspace(start_angle, stop_angle, 200):
        angle = math.radians(deg)
        o_rot = rotate(o, rot_axis, angle)
        d_rot = rotate(d, rot_axis, angle)

        # Find intersection: t = (rect_center - o_rot) · d_mid / (d_rot · d_mid)
        denom = np.dot(d_rot, d_mid)
        if abs(denom) > 1e-10:  # avoid division by zero
            t_val = np.dot(rect_center - o_rot, d_mid) / denom
            intersection = o_rot + t_val * d_rot

            # Project onto perp1/perp2 coordinate system
            rel = intersection - rect_center
            x = np.dot(rel, perp1)
            y = np.dot(rel, perp2)
            intersections_x.append(x)
            intersections_y.append(y)

    # Plot Intersections
    ax2.plot(intersections_x, intersections_y, 'b.-')
    ax2.set_xlabel("Screen X / m (horizontal)")
    ax2.set_ylabel("Screen Y / m (vertical)")
    ax2.set_title("Line of sight on Simulator Screen")
    ax2.set_aspect('equal')
    ax2.grid(True)

    # Calculate segment lengths and x displacements
    segment_lengths = []
    x_displacements = []
    for i in range(1, len(intersections_x)):
        dx = intersections_x[i] - intersections_x[i - 1]
        dy = intersections_y[i] - intersections_y[i - 1]
        x_displacements.append(dx)
        segment_lengths.append(math.sqrt(dx * dx + dy * dy))

    # Calculate velocity assuming an angular velocity of 15 arcsec/sec for rotation around rot_axis.
    # The cosine for dec is already accounted for by the simulation of lines of sights on the screen.
    n_samples = len(intersections_x)
    angular_step_deg = abs(stop_angle - start_angle) / (n_samples - 1)
    angular_step_arcsec = angular_step_deg * 3600
    sidereal_rate = 15.041  # arcsec/sec
    time_per_step_s = angular_step_arcsec / sidereal_rate
    velocities_mm_s = [length / time_per_step_s * 1000.0 for length in segment_lengths]
    x_velocities_mm_s = [dx / time_per_step_s * 1000.0 for dx in x_displacements]

    # Convert X velocity to px/s using screen configuration
    pixels_per_mm = args.screen_width_px / args.screen_width_mm
    x_velocities_px_s = [v * pixels_per_mm for v in x_velocities_mm_s]

    # Create percentage x-axis (0% to 100%)
    n_velocity_samples = len(velocities_mm_s)
    percent_x = [i * 100.0 / (n_velocity_samples - 1) for i in range(n_velocity_samples)]

    ax3.plot(percent_x, velocities_mm_s, 'r.-', label='Total velocity (mm/s)')

    ax4.plot(percent_x, x_velocities_px_s, 'b.-', label='X velocity (px/s)')

    # Calculate and plot sidereal velocity at this distance for comparison
    # Convert to rad/s: 15.041 * (pi/180) / 3600 rad/s
    sidereal_rate_rad_s = sidereal_rate * math.pi / (180 * 3600)  # rad/s
    # Velocity = angular_velocity * distance
    sidereal_velocity_mm_s = sidereal_rate_rad_s * abs(args.distance) * 1000.0 * math.cos(dec if dec is not None else 0)
    ax3.axhline(y=sidereal_velocity_mm_s, color='green', linestyle='--',
                label=f'Sidereal velocity: {sidereal_velocity_mm_s:.4g} mm/s')

    ax3.set_xlabel("Progress (%)")
    ax3.set_ylabel("Velocity (mm/s)")
    ax3.set_title("Velocity of line of sight on screen")
    ax3.legend()
    ax3.grid(True)

    ax4.set_xlabel("Progress (%)")
    ax4.set_ylabel("X Velocity (px/s)")
    ax4.set_title("X velocity (horizontal) on screen")
    ax4.legend()
    ax4.grid(True)

    fig2.tight_layout()

    try:
        plt.show()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
