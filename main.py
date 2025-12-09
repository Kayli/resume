
import os
import yaml

from pdf_builder import build_pdf
from sanitizer import sanitize_data


def load_data(path=None):
    """Load and validate YAML resume data from path (defaults to repo data.yaml).

    Raises FileNotFoundError or ValueError on error.
    Returns the parsed data mapping.
    """
    here = os.path.dirname(__file__)
    yaml_path = path or os.path.join(here, 'data.yaml')
    if not os.path.exists(yaml_path):
        raise FileNotFoundError('data.yaml was not found in the repository root.')

    with open(yaml_path, 'r', encoding='utf-8') as yf:
        data = yaml.safe_load(yf) or {}
    # Ensure data is present and is a mapping; fail fast with a clear message.
    if not isinstance(data, dict) or not data:
        raise ValueError('data.yaml is empty or malformed - expected a mapping with resume data')
    return data


def main():
    data = load_data()
    data = sanitize_data(data)
    build_pdf("Resume-Illia-Karpenkov.pdf", data)
    build_pdf("Resume-Illia-Karpenkov-short.pdf", data, max_roles=7)


if __name__ == '__main__':
    main()
