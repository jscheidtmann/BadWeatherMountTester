# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Features
- Southern Hemisphere support: star moves right-to-left, UI and instructions
  adapt accordingly.
- Velocity override entry (px/s) in simulation control: enter the simulation
  velocity directly in simulator pixels per second instead of a PHD2 drift rate.
  Applied via an "Apply" button; "Clear" restores the measured velocity.
  (`/api/simulation/velocity` POST/DELETE endpoints; config field
  `sim_velocity_override_px_s`).
- Average velocity fallback: if only one or two stripes are timed (not all
  three), their average is used instead of falling back to the sidereal
  estimate.
- "Current Config" link in the navigation bar between Back and Next, opening
  the configuration download in a new browser tab.
- `/config` GET endpoint: downloads the complete current configuration as a
  YAML text file (`setup.yml`). 

#### Developer Experience
- Logging facilities: application now writes log files in the current working
  directory.
- `--locale` CLI parameter to override the system / browser language
  selection.
- `justfile` with `build`, `clean`, and `full-clean` recipes for common
  development tasks; `full-clean` works on Windows.
- Manual workflow to publish documentation to GitHub Pages. 

### Changed
- Simulation velocity source label shows "manual override" (green) when a
  velocity override is active, "interpolated" when all three stripes are
  measured, "partial average" when some are missing, and "estimated" as
  fallback.

### Fixed
- Pre-commit hook failed on Windows.
- PyPI readme logo not displayed because relative image URLs were used;
  switched to full URLs. 

### Internationalization
- German and French translations added for all UI strings. 
- Simulator screen strings (status messages, stripe labels) translated for
  DE and FR.
- Documentation improvements for Southern Hemisphere users in EN, with
  tip call-outs.

### Tried, but ...
- Entry field for "Drift rate" as calculated by PHD2 Log Viewer. Turned out to 
  be hard to convert to screen units. A direct entry field for the px/s 
  simulator velocity is much easier to tune and understand by users.

### Documentation
- Velocity sources described in the manual (measured, interpolated, average,
  estimated, manual override).

### Dependencies
- ruff 0.15.1 → 0.15.2
- pyinstaller 6.18.0 → 6.19.0

---

## [0.8.0] - 2026-02-20

_Initial public release._

[Unreleased]: https://github.com/jscheidtmann/BadWeatherMountTester/compare/release-0.8.0...HEAD
[0.8.0]: https://github.com/jscheidtmann/BadWeatherMountTester/releases/tag/release-0.8.0
