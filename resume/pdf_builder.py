from datetime import datetime
from fpdf import FPDF
from .sanitizer import safe_text
from resume.repository import EmploymentType, ResumeSchema, RoleSchema, HeaderSchema


def render_header(pdf: FPDF, header_data: HeaderSchema):
    ensure_page_open(pdf)
    """Render header on the current page (only call on first page)."""

    page_no = pdf.page_no() or 1
    if page_no > 1:
        return

    name = header_data.name or ''
    title = header_data.title or ''
    contact = header_data.contact or ''

    tagline = ''
    if not name and title:
        if ' - ' in title:
            parts = title.split(' - ', 1)
            name = parts[0].strip()
            tagline = parts[1].strip()
        else:
            name = title

    pdf.set_y(12)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 8, safe_text(name), ln=1, align='C')

    if tagline:
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 6, safe_text(tagline), ln=1, align='C')
    elif title != name:
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 6, safe_text(title), ln=1, align='C')

    if contact:
        pdf.set_font('Arial', '', 9)
        pdf.cell(0, 5, safe_text(contact), ln=1, align='C')

    pdf.ln(2)
    pdf.set_draw_color(50, 50, 50)
    pdf.set_line_width(0.25)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)


def render_footer(pdf: FPDF):
    pdf.set_y(-12)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.25)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 8, f'Page {pdf.page_no()}', 0, 0, 'C')


def format_date(date_str):
    if not date_str:
        return ""
    # Parse ISO-style date
    dt = datetime.strptime(date_str, "%Y-%m")
    return dt.strftime("%b %Y")  # 'Oct 2023'


def add_job_entry(pdf: FPDF, header_data: HeaderSchema, role: RoleSchema):
    ensure_page_open(pdf)
    full_width = pdf.w - pdf.l_margin - pdf.r_margin

    # Title
    pdf.set_font('Arial', 'B', 12)
    title_text = safe_text(role.role)
    pdf.cell(0, 6, title_text, ln=0, align='L')

    # Dates on the right
    pdf.set_font('Arial', '', 10)
    start = format_date(role.start)
    end = format_date(role.end) if role.end else "Present"
    dates_text = f"{start} - {end}"
    
    # Move cursor to right margin minus text width
    pdf.set_x(pdf.w - pdf.r_margin - pdf.get_string_width(dates_text))
    pdf.cell(pdf.get_string_width(dates_text), 6, dates_text, ln=1, align='R')

    # Company + location
    pdf.set_font('Arial', 'I', 10)
    location_parts = [role.location.strip()] if role.location else []
    markers = []
    if role.is_hybrid:
        markers.append('Hybrid')
    if role.employment == EmploymentType.CONTRACT:
        markers.append('Contract')
    if markers:
        location_parts.append(", ".join(markers))
    location_text = " (" + ", ".join(location_parts) + ")" if location_parts else ""
    pdf.cell(0, 6, f"{role.company}{location_text}", ln=1, align='L')

    # Body / bullets
    pdf.set_font('Arial', '', 10)
    full_width = pdf.w - pdf.l_margin - pdf.r_margin
    for paragraph in role.done.split('\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            pdf.ln(2)
            continue
        if paragraph.startswith('-'):
            content = paragraph.lstrip('-').strip()
            indent = 6
            bullet = '- '
            pdf.set_x(pdf.l_margin + indent)
            pdf.cell(6, 5, bullet, 0, 0)
            pdf.multi_cell(full_width - indent - 6, 5, content)
        else:
            pdf.multi_cell(full_width, 5, paragraph)
    pdf.ln(2)

    # Stack
    if role.stack:
        pdf.set_font('Arial', 'I', 9)
        pdf.multi_cell(full_width, 5, safe_text(f"Stack: {role.stack}"))
    pdf.ln(6)
    

def add_job_entry2(
    pdf: FPDF,
    header_data: HeaderSchema,
    role: RoleSchema
):
    ensure_page_open(pdf)
    title_font = ('Arial', 'B', 12)
    dates_font = ('Arial', '', 10)
    sub_font = ('Arial', 'I', 10)
    body_font = ('Arial', '', 10)
    gap_after = 6
    full_width = pdf.w - pdf.l_margin - pdf.r_margin

    if pdf.get_y() > pdf.h - pdf.b_margin - 60:
        render_footer(pdf)
        pdf.add_page()
        render_header(pdf, header_data)

    pdf.set_font(*title_font)

    pdf.cell(0, 6, safe_text(role.role), 0, 0, 'L')
    pdf.set_font(*dates_font)
    start = format_date(role.start)
    end = format_date(role.end) if role.end else "Present"

    dates = f"{start} - {end}"  # en-dash
    pdf.set_font(*dates_font)
    pdf.cell(-pdf.l_margin, 6, dates, 0, 1, 'R')
    
    pdf.set_font(*sub_font)
    base_location = role.location.strip()
    markers = []
    if role.is_hybrid:
        markers.append('Hybrid')
    
    if role.employment == EmploymentType.CONTRACT:
        markers.append('Contract')

    if base_location:
        location_details = f"{base_location} ({', '.join(markers)})" if markers else base_location
    else:
        location_details = f"({', '.join(markers)})" if markers else ''

    company_line = f"{role.company} - {location_details}" if location_details else role.company
    pdf.cell(0, 6, safe_text(company_line), 0, 1, 'L')

    pdf.set_font(*body_font)
    for paragraph in role.done.split('\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            pdf.ln(2)
            continue
        if paragraph.startswith('-'):
            content = paragraph.lstrip('-').strip()
            indent = 6
            bullet = '- '
            pdf.set_x(pdf.l_margin + indent)
            pdf.cell(6, 5, bullet, 0, 0)
            pdf.multi_cell(full_width - indent - 6, 5, content)
        else:
            pdf.multi_cell(full_width, 5, paragraph)
    pdf.ln(2)

    if role.stack:
        pdf.set_font('Arial', 'I', 9)
        pdf.multi_cell(full_width, 5, safe_text(f"Stack: {role.stack}"))
    pdf.ln(gap_after)


def build_pdf(output_path: str, data_map: ResumeSchema, max_roles: int | None = None):
    pdf = FPDF()
    header = data_map.header
    roles = list(data_map.roles or [])
    if max_roles is not None:
        roles = roles[:max_roles]

    contact_line = f"Email: {header.email} | Mobile: {header.phone} | Vancouver, BC"
    header.contact = contact_line

    pdf.add_page()
    render_header(pdf, header)
    pdf.set_auto_page_break(True)

    for role in roles:
        add_job_entry(
            pdf,
            header,
            role
        )

    render_footer(pdf)
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")


def ensure_page_open(pdf: FPDF):
    if pdf.page_no() == 0:
        pdf.add_page()
