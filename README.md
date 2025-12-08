This project generates a PDF resume from structured YAML data (`data.yaml`).

How to use

1. Create a Python virtual environment and install dependencies (FPDF, PyYAML).

   python -m venv .venv
   source .venv/bin/activate
   pip install fpdf pyyaml

2. Run the generator:

   python main.py

Output

- The script writes `Resume-Illia-Karpenkov.pdf` to the repository root.

Notes

- The generator uses the `data.yaml` file. Edit it to change header and roles.
- The PDF renderer uses Latin-1 encoding; non-ASCII characters are sanitized in the header and body bullets are ASCII-friendly.
