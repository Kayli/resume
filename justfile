# justfile

# default shell
set shell := ["bash", "-ceu"]

default: main

# Only run install if marker file doesn't exist
install:
    @if [ ! -f ".venv/.installed" ]; then \
        echo "Installing uv and setting up .venv..."; \
        curl -LsSf https://astral.sh/uv/install.sh | sh; \
        uv venv .venv; \
        .venv/bin/python -m ensurepip --upgrade; \
        .venv/bin/python -m pip install --upgrade pip; \
        .venv/bin/pip3 install -r requirements.txt; \
        touch .venv/.installed; \
    else \
        echo ".venv already installed, skipping"; \
    fi

# Run static type checks (mypy) and pytest
test: install
    @echo "Running mypy on resume and tests..."
    .venv/bin/python -m mypy ./resume
    .venv/bin/python -m mypy ./tests
    @echo "Running pytest..."
    .venv/bin/python -m pytest -q

# Generate resume PDF
main: install
    @echo "Running main.py to generate resume PDF..."
    .venv/bin/python main.py
