This project generates a PDF resume from structured YAML data (`data.yaml`).

How to use

1. Create a Python virtual environment and install dependencies. The required packages are listed in `requirements.txt`.

   python -m venv .venv
   source .venv/bin/activate
      # This project is tested on Python 3.9; see `pyproject.toml` for the required Python range.
      pip install -r requirements.txt

2. Run the generator:

   python main.py

Output

- The script writes `Resume-Illia-Karpenkov.pdf` to the repository root.

Notes

- The generator uses the `data.yaml` file. Edit it to change header and roles.
- The PDF renderer uses Latin-1 encoding; non-ASCII characters are sanitized in the header and body bullets are ASCII-friendly.
