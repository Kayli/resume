from flask import Flask, render_template, send_file
import io
import tempfile
import os

from resume.repository import load_data
from resume.sanitizer import sanitize_data
from resume.pdf_builder import build_pdf

app = Flask(__name__)


@app.route("/")
def index():
    data = sanitize_data(load_data())
    return render_template("index.html", header=data.header, roles=data.roles)


@app.route("/download")
def download():
    data = sanitize_data(load_data())
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        build_pdf(tmp_path, data)
        with open(tmp_path, "rb") as f:
            pdf_bytes = io.BytesIO(f.read())
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
    pdf_bytes.seek(0)
    return send_file(
        pdf_bytes,
        as_attachment=True,
        download_name="Resume-Illia-Karpenkov.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
