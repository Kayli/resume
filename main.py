import os
from datetime import datetime
from pathlib import Path

from resume.repository import load_data
from resume.pdf_builder import build_pdf
from resume.sanitizer import sanitize_data


def rotate(path: str):
    p = Path(path)
    if p.exists():
        ts = datetime.now().strftime("%Y-%m-%d")
        rotated = p.with_name(f"{p.stem}-{ts}{p.suffix}")

        # Avoid double-clobbering if multiple runs happen same day
        counter = 1
        while rotated.exists():
            rotated = p.with_name(f"{p.stem}-{ts}-{counter}{p.suffix}")
            counter += 1

        p.rename(rotated)


def main():
    data = load_data()
    data = sanitize_data(data)

    out_dir = os.path.join(os.path.dirname(__file__), "generated")
    os.makedirs(out_dir, exist_ok=True)

    final = os.path.join(out_dir, "Resume-Illia-Karpenkov.pdf")
    short = os.path.join(out_dir, "Resume-Illia-Karpenkov-short.pdf")

    rotate(final)
    build_pdf(final, data)

    rotate(short)
    build_pdf(short, data, max_roles=7)


if __name__ == '__main__':
    main()
