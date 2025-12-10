import os
from fpdf import FPDF
import pytest
from resume.pdf_builder import render_header, render_footer, add_job_entry, build_pdf
import pypdf
import re
from resume.repository import HeaderSchema, RoleSchema, EmploymentType

@pytest.fixture
def pdf():
    return FPDF()

@pytest.fixture
def header_data():
    data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '123-456-7890',
        'title': 'Software Engineer'
    }
    # Validate against HeaderSchema
    HeaderSchema(**data)
    return data

@pytest.fixture
def role_data():
    data = {
        'role': 'Software Engineer',
        'company': 'Tech Corp',
        'employment': 'full-time',
        'is_hybrid': True,
        'dates': 'Jan 2020 - Dec 2025',
        'location': 'Vancouver, BC',
        'done': '- Developed software\n- Led projects',
        'stack': 'Python, JavaScript'
    }
    # Validate against RoleSchema
    # Provide start/end in YYYY-MM format to satisfy RoleSchema while keeping 'dates' for pdf rendering
    data['start'] = '2020-01'
    data['end'] = '2025-12'
    data['employment'] = EmploymentType.PERMANENT  # Adjust to match schema enum
    RoleSchema(**data)
    return data

def extract_text_from_pdf(pdf):
    """Helper function to extract text from an FPDF object using a system temp file."""
    import tempfile
    # Use a NamedTemporaryFile so the file is created in the system temp dir
    # and is automatically removed on close. Set delete=False because
    # pypdf opens the file independently on some platforms.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        pdf.output(tmp_path)
        with open(tmp_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return "\n".join(page.extract_text() for page in reader.pages)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

def normalize_text(text):
    """Normalize text by removing extra spaces and line breaks."""
    return re.sub(r"\s+", " ", text.strip())


def test_header_name_rendered_correctly(pdf, header_data):
    render_header(pdf, header_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert header_data['name'] in pdf_text

def test_header_title_rendered_correctly(pdf, header_data):
    render_header(pdf, header_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert header_data['title'] in pdf_text

def test_footer_page_number_rendered_correctly(pdf):
    pdf.add_page()
    render_footer(pdf)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert "Page 1" in pdf_text

def test_job_entry_role_rendered_correctly(pdf, header_data, role_data):
    add_job_entry(pdf, header_data,
                  role_data['role'],
                  role_data['company'],
                  role_data['employment'],
                  role_data['is_hybrid'],
                  role_data['dates'],
                  role_data['location'],
                  role_data['done'],
                  role_data['stack'])
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert normalize_text(role_data['role']) in pdf_text

def test_job_entry_company_rendered_correctly(pdf, header_data, role_data):
    add_job_entry(pdf, header_data,
                  role_data['role'],
                  role_data['company'],
                  role_data['employment'],
                  role_data['is_hybrid'],
                  role_data['dates'],
                  role_data['location'],
                  role_data['done'],
                  role_data['stack'])
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert normalize_text(role_data['company']) in pdf_text

def test_job_entry_dates_rendered_correctly(pdf, header_data, role_data):
    add_job_entry(pdf, header_data,
                  role_data['role'],
                  role_data['company'],
                  role_data['employment'],
                  role_data['is_hybrid'],
                  role_data['dates'],
                  role_data['location'],
                  role_data['done'],
                  role_data['stack'])
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert normalize_text(role_data['dates']) in pdf_text

def test_pdf_header_data_rendered_correctly(tmp_path, header_data):
    output_path = tmp_path / "test_resume.pdf"
    data_map = {
        'header': header_data,
        'roles': []
    }
    build_pdf(output_path, data_map)
    with open(output_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        pdf_text = normalize_text("\n".join(page.extract_text() for page in reader.pages))
        assert header_data['name'] in pdf_text
        assert header_data['title'] in pdf_text

def test_pdf_role_data_rendered_correctly(tmp_path, header_data, role_data):
    output_path = tmp_path / "test_resume.pdf"
    data_map = {
        'header': header_data,
        'roles': [role_data]
    }
    build_pdf(output_path, data_map)
    with open(output_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        pdf_text = normalize_text("\n".join(page.extract_text() for page in reader.pages))
        assert normalize_text(role_data['role']) in pdf_text
        assert normalize_text(role_data['company']) in pdf_text
        assert normalize_text(role_data['dates']) in pdf_text
