import os
from fpdf import FPDF
import pytest
from resume.pdf_builder import render_header, render_footer, add_job_entry, build_pdf
import pypdf
import re

@pytest.fixture
def pdf():
    return FPDF()

@pytest.fixture
def header_data():
    return {
        'title': 'John Doe - Software Engineer',
        'contact': 'Email: john.doe@example.com | Mobile: 123-456-7890 | Vancouver, BC'
    }

@pytest.fixture
def role_data():
    return {
        'role': 'Software Engineer',
        'company': 'Tech Corp',
        'employment': 'full-time',
        'is_hybrid': True,
        'dates': 'Jan 2020 - Dec 2025',
        'location': 'Vancouver, BC',
        'done': '- Developed software\n- Led projects',
        'stack': 'Python, JavaScript'
    }

def extract_text_from_pdf(pdf):
    """Helper function to extract text from an FPDF object."""
    pdf.output("temp.pdf")
    with open("temp.pdf", "rb") as f:
        reader = pypdf.PdfReader(f)
        return "\n".join(page.extract_text() for page in reader.pages)

def normalize_text(text):
    """Normalize text by removing extra spaces and line breaks."""
    return re.sub(r"\s+", " ", text.strip())

def test_render_header(pdf, header_data):
    render_header(pdf, header_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    # Adjusted expected text to match extracted text format
    assert "John Doe Software Engineer" in pdf_text
    assert normalize_text(header_data['contact']) in pdf_text

def test_render_footer(pdf):
    pdf.add_page()  # Ensure a page is open before rendering the footer
    render_footer(pdf)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    # Verify that footer data is rendered
    assert f"Page 1" in pdf_text  # Adjusted to match the actual page number

def test_add_job_entry(pdf, header_data, role_data):
    add_job_entry(pdf, header_data, **role_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    # Verify that role data is rendered
    assert normalize_text(role_data['role']) in pdf_text
    assert normalize_text(role_data['company']) in pdf_text
    assert normalize_text(role_data['dates']) in pdf_text

def test_build_pdf(tmp_path, header_data, role_data):
    output_path = tmp_path / "test_resume.pdf"
    data_map = {
        'header': header_data,
        'roles': [role_data]
    }
    build_pdf(output_path, data_map)
    assert os.path.exists(output_path)  # Ensure the PDF file is created

    # Verify that header and role data are rendered in the PDF
    with open(output_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        pdf_text = normalize_text("\n".join(page.extract_text() for page in reader.pages))
        # Adjusted expected text to match extracted text format
        assert "John Doe Software Engineer" in pdf_text
        assert normalize_text(header_data['contact']) in pdf_text
        assert normalize_text(role_data['role']) in pdf_text
        assert normalize_text(role_data['company']) in pdf_text
        assert normalize_text(role_data['dates']) in pdf_text
