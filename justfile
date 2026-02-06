# justfile

# default shell
set shell := ["bash", "-ceu"]

default: run

# Install dependencies globally in the container
install:
    @echo "Installing project dependencies globally in the container..."
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"

# Force installation even if already installed
reinstall:
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]" --upgrade

# Run static type checks (mypy) and pytest
test: install
    @echo "Running mypy on resume and tests..."
    python -m mypy ./resume
    python -m mypy ./tests
    @echo "Running pytest..."
    python -m pytest -q

# Generate resume PDF
run: install
    @echo "Running main.py to generate resume PDF..."
    python main.py
