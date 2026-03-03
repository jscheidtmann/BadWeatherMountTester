# How to contribute to this project

## Suggestings and Bug Reports

If you have suggestions or you need help with an issue, please check the [issues on GitHub](https://github.com/jscheidtmann/BadWeatherMountTester/issues)
and create one issue if necessary.

## Contributing Code

1. Fork the repository and clone your fork
2. Install development dependencies:

   ```bash
   uv sync --dev
   ```

3. Install [just](https://just.systems/) for common development tasks:

   | Platform | Command |
   | -------- | ------- |
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

5. **Internationalization:** The project supports German, English, and French via Flask-Babel. Translation files live in
   `src/badweathermounttester/translations/`. After editing `.po` files run `just compile-translations`.

6. Submit a pull request against `main`

## Contributors

Jens Scheidtmann ([Original Author](https://github.com/jscheidtmann), BDFL)
