# Bad Weather Mount Tester

[![Python application](https://github.com/jscheidtmann/BadWeatherMountTester/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/jscheidtmann/BadWeatherMountTester/actions/workflows/python-app.yml)
[![PyPI version](https://img.shields.io/pypi/v/BadWeatherMountTester)](https://pypi.org/project/BadWeatherMountTester/)
[![GitHub release](https://img.shields.io/github/v/release/jscheidtmann/BadWeatherMountTester)](https://github.com/jscheidtmann/BadWeatherMountTester/releases/latest)
[![Release date](https://img.shields.io/github/release-date/jscheidtmann/BadWeatherMountTester)](https://github.com/jscheidtmann/BadWeatherMountTester/releases/latest)
[![Dependencies](https://img.shields.io/librariesio/release/pypi/BadWeatherMountTester)](https://libraries.io/pypi/BadWeatherMountTester)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jscheidtmann/BadWeatherMountTester/refs/heads/main/docs/BWMT_logo_w.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/jscheidtmann/BadWeatherMountTester/refs/heads/main/docs/BWMT_logo_b.svg">
  <img alt="Bad Weather Mount Tester Logo" src="https://raw.githubusercontent.com/jscheidtmann/BadWeatherMountTester/refs/heads/main/docs/BWMT_logo_b.svg">
</picture>

When you buy a new telescope mount, the first things to do is to measure the periodic error, because if the periodic error is really high, you would like to
complain and send it back as fast as possible. Unfortunately, most of the time there will be bad weather after buying astro gear for an indefinite amount of time.

**Bad Weather Mount Tester to the rescue!**

Using this program you can test the periodic error of your mount any time, any place, provided you have a spare computer and monitor and a little bit of space.

## Documentation

The full user manual is available at <https://jscheidtmann.github.io/BadWeatherMountTester/>.

## How to Install

### From PyPI (all platforms)

Using pip:

```bash
pip install BadWeatherMountTester
```

Or using [pipx](https://pipx.pypa.io/) for an isolated install:

```bash
pipx install BadWeatherMountTester
```

Then run the application:

```bash
bwmt
```

### From GitHub Releases (pre-built binaries)

Download the latest release from the [GitHub Releases](https://github.com/jscheidtmann/BadWeatherMountTester/releases) page.

- **Linux:** Download the `.tar.gz` archive, extract it, and run `./bwmt`
- **Windows:** Download the `.zip` archive, extract it, and run `bwmt.exe`
- **macOS:** Download the `.tar.gz` archive, extract it, and run `./bwmt`

### From Source

```bash
git clone https://github.com/jscheidtmann/BadWeatherMountTester.git
cd BadWeatherMountTester
```

Install [uv](https://docs.astral.sh/uv/) if you don't have it, then:

```bash
uv sync
uv run bwmt
```

## How to Contribute

1. Fork the repository and clone your fork
2. Install development dependencies:
   ```bash
   uv sync --dev
   ```
3. Install [just](https://just.systems/) for common development tasks:

   | Platform | Command |
   |----------|---------|
   | Windows | `winget install Casey.Just` |
   | macOS | `brew install just` |
   | Linux / Raspberry Pi | `curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh \| bash -s -- --to ~/.local/bin` |

4. List all available recipes:
   ```bash
   just
   ```
   Key recipes:

   | Recipe | Description |
   |--------|-------------|
   | `just test` | Run the test suite |
   | `just lint` | Run ruff and flake8 |
   | `just translations` | Extract strings, update `.po` files, compile `.mo` files |
   | `just compile-translations` | Compile `.po` → `.mo` only |
   | `just run` | Run the application |

5. **Internationalization:** The project supports German, English, and French via Flask-Babel. Translation files live in `src/badweathermounttester/translations/`. After editing `.po` files run `just compile-translations`.
6. Submit a pull request against `main`

## CHANGELOG.md

This project keeps a [CHANGELOG](https://github.com/jscheidtmann/BadWeatherMountTester/blob/main/CHANGELOG.md).

# Credit

This software is based on the idea by [Klaus Weyer from Solingen, Germany](https://web.archive.org/web/20241013053734/https://watchgear.de/SWMT/SWMT.html). Rest in Peace, Klaus!

# Author, Copyright & License

Copyright (c) 2026 Jens Scheidtmann and contributors (see CONTRIBUTORS.md)

This file is part of BWMT, the Bad Weather Mount Tester.

BWMT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

BWMT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with BWMT.  If not, see <http://www.gnu.org/licenses/>.
