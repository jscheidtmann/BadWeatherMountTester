import argparse
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="geometry",
        description="Visualize telescope mount geometry and rotation",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=51.0,
        help="Latitude in degrees (default: 51.0)",
    )
    parser.add_argument(
        "-o",
        "--offset",
        type=float,
        default=0.27,
        help="Telescope offset from rotation axis (default: 0.27)",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=0.0,
        help="Start angle in degrees (default: 0.0)",
    )
    parser.add_argument(
        "--stop",
        type=float,
        default=-10.0,
        help="Stop angle in degrees (default: -10.0)",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=float,
        default=-3.41,
        help="Distance from origin along the line (default: 3.41m)",
    )
    parser.add_argument(
        "--dec",
        type=float,
        default=None,
        help="Declination in degrees for line of sight calculation",
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

########
# Preparations
########
args = parse_args()

dec_str = f", Declination: {args.dec}°" if args.dec is not None else ""
print(f"Latitude: {args.lat}°, Offset: {args.offset}m, Start: {args.start}°, Stop: {args.stop}°{dec_str}")

lat = math.radians(args.lat)
dec = math.radians(args.dec) if args.dec is not None else None

# Coordinate system: x in direction of observer, y in direction of screen, z up to the ceiling

# Rotation Axis of the telescope (unit vector)
rot_axis = np.array((0, math.cos(lat), -math.sin(lat)))

# Telescope is affixed off-axis to mount
#  - First component of offset vector is offset from RA-axis (in direction of observer)
#  - Second component is offset from Dec axis, which is zero here (negative is in direction of floor)
o = np.array((args.offset, 0, 0))

# Line of sight direction
# if lat+dec = 90°, pointing straight to the screen.
d = np.array((0, 1, 0))
if dec is not None:
    d = np.array((0, math.cos(math.radians(90)-lat+dec), math.sin(math.radians(90)-lat+dec)))
    # print("Line of sight direction vector:", d)

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

# Rectangle dimensions
width, height = 0.5, 0.3

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
fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(6, 10))

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
        t = np.dot(rect_center - o_rot, d_mid) / denom
        intersection = o_rot + t * d_rot

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

# Calculate segment lengths
segment_lengths = []
for i in range(1, len(intersections_x)):
    dx = intersections_x[i] - intersections_x[i - 1]
    dy = intersections_y[i] - intersections_y[i - 1]
    segment_lengths.append(math.sqrt(dx * dx + dy * dy))

# Calculate velocity assuming angular velocity of 15 arcsec/sec
n_samples = len(intersections_x)
angular_step_deg = abs(stop_angle - start_angle) / (n_samples - 1)
angular_step_arcsec = angular_step_deg * 3600
sidereal_rate = 15.041  # arcsec/sec
time_per_step_s = angular_step_arcsec / sidereal_rate
velocities_m_s = [length / time_per_step_s for length in segment_lengths]

ax3.plot(velocities_m_s, 'r.-')

# # Calculate and plot sidereal velocity at this distance for comparison
# # Sidereal rate: 15.041 arcsec/sec
# # Convert to rad/s: 15.041 * (pi/180) / 3600 rad/s
# sidereal_rate_rad_s = sidereal_rate * math.pi / (180 * 3600)
# # Velocity = angular_velocity * distance
# sidereal_velocity_m_s = sidereal_rate_rad_s * abs(args.distance) * abs(math.cos(math.radians(90)-dec if dec is not None else math.radians(90)-lat))
# ax3.axhline(y=sidereal_velocity_m_s, color='green', linestyle='--', 
#            label=f'Sidereal velocity: {sidereal_velocity_m_s:.4f} m/s')


ax3.set_xlabel("Sample")
ax3.set_ylabel("Velocity (m/s)")
ax3.set_title("Velocity of line of sight on screen / m/s")
ax3.legend()
ax3.grid(True)

fig2.tight_layout()

plt.show()
