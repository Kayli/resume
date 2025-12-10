from fpdf import FPDF
from .sanitizer import safe_text
from resume.repository import ResumeSchema, RoleSchema


def render_header(pdf, header_data):
    ensure_page_open(pdf)
    """Render header on the current page (only call on first page).

    header_data is expected to be a HeaderSchema instance (Pydantic model).
    """
    try:
        page_no = pdf.page_no()
    except Exception:
        page_no = 1
    if page_no > 1:
        return

    name = getattr(header_data, 'name', '') or ''
    title = getattr(header_data, 'title', '') or ''
    contact = getattr(header_data, 'contact', '') if hasattr(header_data, 'contact') else ''

    tagline = ''  # Ensure tagline is always initialized
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
    elif title and title != name:
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


def render_footer(pdf):
    pdf.set_y(-12)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.25)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 8, f'Page {pdf.page_no()}', 0, 0, 'C')


def add_job_entry(pdf, header_data, role, company, employment, is_hybrid, dates, location, done, stack):
    ensure_page_open(pdf)
    """Render a single job entry to the provided FPDF instance.

    If a page break is needed, render footer for current page, add a new page,
    and render header for the new page.
    """
    title_font = ('Arial', 'B', 12)
    dates_font = ('Arial', '', 10)
    sub_font = ('Arial', 'I', 10)
    body_font = ('Arial', '', 10)
    gap_after = 6

    full_width = pdf.w - pdf.l_margin - pdf.r_margin

    # if remaining space is small, finish current page and start a new one
    if pdf.get_y() > pdf.h - pdf.b_margin - 60:
        render_footer(pdf)
        pdf.add_page()
        render_header(pdf, header_data)

    pdf.set_font(*title_font)
    pdf.cell(0, 6, safe_text(role), 0, 0, 'L')
    pdf.set_font(*dates_font)
    pdf.cell(-pdf.l_margin, 6, safe_text(dates), 0, 1, 'R')

    pdf.set_font(*sub_font)
    base_location = (location or '').strip()
    markers = []
    if is_hybrid:
        markers.append('Hybrid')
    # employment may be an enum value
    try:
        emp_val = employment.value if hasattr(employment, 'value') else employment
    except Exception:
        emp_val = employment
    if emp_val == 'contract' or emp_val == 'Contract':
        markers.append('Contract')

    if base_location:
        location_details = f"{base_location} ({', '.join(markers)})" if markers else base_location
    else:
        location_details = f"({', '.join(markers)})" if markers else ''

    company_line = f"{company} - {location_details}" if location_details else company
    pdf.cell(0, 6, safe_text(company_line), 0, 1, 'L')

    pdf.set_font(*body_font)
    for paragraph in done.split('\n'):
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

    if stack:
        pdf.set_font('Arial', 'I', 9)
        pdf.multi_cell(full_width, 5, safe_text(f"Stack: {stack}"))
    pdf.ln(gap_after)


def build_pdf(output_path, data_map, max_roles=None):
    """Build PDF using a single sanitized data mapping.

    - data_map is the sanitized data dict (has 'header' and 'roles').
    - max_roles: if provided, only the first N roles are included (for one-page output).
    """
    pdf = FPDF()
    # data_map is expected to be a ResumeSchema instance
    header = getattr(data_map, 'header')
    roles = list(getattr(data_map, 'roles') or [])
    if max_roles is not None:
        roles = roles[:max_roles]

    contact_line = (
        f"Email: {getattr(header, 'email', 'N/A')} | "
        f"Mobile: {getattr(header, 'phone', 'N/A')} | "
        f"Vancouver, BC"
    )
    setattr(header, 'contact', contact_line)

    pdf.add_page()
    render_header(pdf, header)
    pdf.set_auto_page_break(True)

    for role in roles:
        # role is a RoleSchema instance
        add_job_entry(pdf, header,
                      getattr(role, 'role', ''),
                      getattr(role, 'company', ''),
                      getattr(role, 'employment', ''),
                      getattr(role, 'is_hybrid', False) if hasattr(role, 'is_hybrid') else False,
                      getattr(role, 'dates', '') if hasattr(role, 'dates') else '',
                      getattr(role, 'location', ''),
                      getattr(role, 'done', ''),
                      getattr(role, 'stack', ''))

    # render footer for the last page
    render_footer(pdf)
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")


def ensure_page_open(pdf):
    """Ensure that a page is open in the PDF instance."""
    if pdf.page_no() == 0:
        pdf.add_page()
