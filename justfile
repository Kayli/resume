# justfile

# Set the default shell to bash with options:
# -c: Execute the command string
# -e: Exit immediately if a command exits with a non-zero status (error)
# -u: Treat unset variables as an error and exit
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

# Check CI/CD status
ci-status:
    @echo "Checking recent CI/CD runs..."
    gh run list --limit 5

# Test that shell options (-ceu) are working
test-shell:
    @echo "Testing -u (error on unset variable)..."
    @echo "Attempting to access: ${UNDEFINED_VAR}" && echo "FAIL: -u not working"
    
test-shell-e:
    @echo "Testing -e (exit on error)..."
    @false && echo "FAIL: -e not working"
