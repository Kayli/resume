import os

from resume.repository import load_data
from resume.pdf_builder import build_pdf
from resume.sanitizer import sanitize_data


def main():
    data = load_data()
    data = sanitize_data(data)

    out_dir = os.path.join(os.path.dirname(__file__), 'generated')
    os.makedirs(out_dir, exist_ok=True)
    build_pdf(os.path.join(out_dir, "Resume-Illia-Karpenkov.pdf"), data)
    build_pdf(os.path.join(out_dir, "Resume-Illia-Karpenkov-short.pdf"), data, max_roles=7)


if __name__ == '__main__':
    main()
