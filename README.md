# PDF Resume Generator

This project generates a PDF resume from structured YAML data.

## How to use

### 1. Set up the environment and install dependencies

The `install` task will create a `.venv`, install packages from `requirements.txt`, and mark the environment as installed:

just install

- To force reinstallation (clean environment), run:

just reinstall

### 2. Run the generator

just run

or directly:

.venv/bin/python main.py

## Output

- The script writes `Resume-Illia-Karpenkov.pdf` to the repository root.

## Notes

- The generator uses `data.yaml` for header and role information. Edit this file to change the resume content.
- The PDF renderer uses Latin-1 encoding; non-ASCII characters in the header are sanitized, and body bullets are ASCII-friendly.

## Run tests and static checks

- The `test` task runs mypy type checks and pytest:

just test

## Pending questions

- Handling Pydantic internal exceptions during `BaseModel` definition  
  See discussion: [pydantic/pydantic#12621](https://github.com/pydantic/pydantic/discussions/12621)
