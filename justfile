set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List available recipes
default:
    @just --list

# Run tests
test:
    uv run pytest

# Lint
lint:
    uv run flake8 src/
    uv run ruff check src/

# Extract translatable strings from source into the .pot template
extract:
    uv run pybabel extract -F babel.cfg -o src/badweathermounttester/translations/messages.pot src/

# Update existing .po files from the .pot template (run after extract)
update-translations: extract
    uv run pybabel update -i src/badweathermounttester/translations/messages.pot -d src/badweathermounttester/translations

# Compile .po → .mo (must run before translations take effect)
compile-translations:
    uv run pybabel compile -d src/badweathermounttester/translations

# Full translation refresh: extract, update .po files, compile .mo files
translations: update-translations compile-translations

# Remove log files and other temporary files
clean:
    rm bwmt*.log

# Remove build artifacts
full-clean: clean
    rm dist 
    rm build 

# Run the application
run:
    uv run bwmt
