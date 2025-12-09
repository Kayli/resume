from fpdf import FPDF
from .sanitizer import safe_text


def render_header(pdf, header_data):
    """Render header on the current page (only call on first page)."""
    try:
        page_no = pdf.page_no()
    except Exception:
        page_no = 1
    if page_no > 1:
        return

    title = header_data.get('title', '')
    contact = header_data.get('contact', '')
    if not title and not contact:
        return
    name = title
    tagline = ''
    if ' - ' in title:
        parts = title.split(' - ', 1)
        name = parts[0].strip()
        tagline = parts[1].strip()

    pdf.set_y(12)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 8, safe_text(name), ln=1, align='C')
    if tagline:
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 6, safe_text(tagline), ln=1, align='C')
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


def add_job_entry(pdf, header_data, role, company, dates, location, done, stack):
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
    pdf.cell(0, 6, f"{role}", 0, 0, 'L')
    pdf.set_font(*dates_font)
    pdf.cell(-pdf.l_margin, 6, f"{dates}", 0, 1, 'R')

    pdf.set_font(*sub_font)
    company_line = f"{company} - {location}" if location else company
    pdf.cell(0, 6, company_line, 0, 1, 'L')

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
    header = data_map.get('header', {}) or {}
    roles = (data_map.get('roles', []) or [])
    if max_roles is not None:
        roles = roles[:max_roles]

    pdf.add_page()
    render_header(pdf, header)
    pdf.set_auto_page_break(True)

    for role in roles:
        add_job_entry(pdf, header,
                      role.get('role', ''),
                      role.get('company', ''),
                      role.get('dates', ''),
                      role.get('location', ''),
                      role.get('done', ''),
                      role.get('stack', ''))

    # render footer for the last page
    render_footer(pdf)
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
