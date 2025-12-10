This project generates a PDF resume from structured YAML data (`data.yaml`).

How to use

1. Set up the environment and install dependencies using doit. The `install` task will create a `.venv` and install packages from `requirements.txt`:

   doit install

2. Run the generator:

   .venv/bin/python main.py
   or
   doit generate

Output

- The script writes `Resume-Illia-Karpenkov.pdf` to the repository root.

Notes

- The generator uses the `data.yaml` file. Edit it to change header and roles.
- The PDF renderer uses Latin-1 encoding; non-ASCII characters are sanitized in the header and body bullets are ASCII-friendly.

Run tests and static checks

- Run the full pipeline (mypy then pytest):

   doit test

