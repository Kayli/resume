import os
from fpdf import FPDF
import pytest
from resume.pdf_builder import render_header, render_footer, add_job_entry, build_pdf, format_date
import pypdf
import re
from resume.repository import HeaderSchema, RoleSchema, EmploymentType, ResumeSchema

@pytest.fixture
def pdf():
    return FPDF()

@pytest.fixture
def header_data():
    return HeaderSchema(
        name='John Doe',
        email='john.doe@example.com',
        phone='123-456-7890',
        title='Software Engineer'
    )

@pytest.fixture
def role_data():
    role = RoleSchema(
        role='Software Engineer',
        company='Tech Corp',
        employment=EmploymentType.PERMANENT,
        is_hybrid=True,
        start='2020-01',
        end='2025-12',
        location='Vancouver, BC',
        done='- Developed software\n- Led projects',
        stack='Python, JavaScript'
    )
    return role

def extract_text_from_pdf(pdf):
    """Helper to extract text from FPDF object."""
    import tempfile
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
    return re.sub(r"\s+", " ", text.strip())

# Header tests
def test_header_name_rendered_correctly(pdf, header_data):
    render_header(pdf, header_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert header_data.name in pdf_text

def test_header_title_rendered_correctly(pdf, header_data):
    render_header(pdf, header_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert header_data.title in pdf_text

# Footer test
def test_footer_page_number_rendered_correctly(pdf):
    pdf.add_page()
    render_footer(pdf)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert "Page 1" in pdf_text

# Job entry tests
def test_job_entry_role_rendered_correctly(pdf, header_data, role_data):
    add_job_entry(pdf, header_data, role_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert normalize_text(role_data.role) in pdf_text

def test_job_entry_company_rendered_correctly(pdf, header_data, role_data):
    add_job_entry(pdf, header_data, role_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    assert normalize_text(role_data.company) in pdf_text

def test_job_entry_dates_rendered_correctly(pdf, header_data, role_data):
    add_job_entry(pdf, header_data, role_data)
    pdf_text = normalize_text(extract_text_from_pdf(pdf))
    dates_text = f"{format_date(role_data.start)} - {format_date(role_data.end)}"
    assert normalize_text(dates_text) in pdf_text

# Full PDF tests
def test_pdf_header_data_rendered_correctly(tmp_path, header_data):
    output_path = tmp_path / "test_resume.pdf"
    data_map = ResumeSchema(header=header_data, roles=[])
    build_pdf(output_path, data_map)
    with open(output_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        pdf_text = normalize_text("\n".join(page.extract_text() for page in reader.pages))
        assert header_data.name in pdf_text
        assert header_data.title in pdf_text
