from fpdf import FPDF
import os

import yaml

def render_header(pdf, header_data):
    """Render header on the current page (only call on first page)."""
    # Only render header on the first page
    try:
        page_no = pdf.page_no()
    except Exception:
        # FPDF may not have page_no yet; defensively assume first page
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


def safe_text(text):
    # robust low-level replacer; accept non-str and None
    if text is None:
        return ''
    s = str(text)
    return s.replace("–", "-").replace("—", "-").replace("’", "'")


def sanitize_value(v):
    """Convert a value to a safe string suitable for PDF rendering."""
    if v is None:
        return ''
    return safe_text(v)


def sanitize_data(data):
    """Return (sanitized_header, sanitized_roles) from loaded YAML data.

    Applies sanitize_value to header fields and to expected role fields.
    """
    sanitized = {}
    sanitized['header'] = {}
    for k, v in (data.get('header', {}) or {}).items():
        sanitized['header'][k] = sanitize_value(v)

    sanitized['roles'] = []
    for r in (data.get('roles', []) or []):
        # Prefer explicit start/end fields; fall back to legacy free-text 'dates'
        start = r.get('start')
        end = r.get('end')
        legacy = r.get('dates')

        disp = ''
        if start or end:
            # Normalize start/end to human readable form. Use YYYY-MM or YYYY where available.
            def fmt(d):
                if d is None:
                    return None
                s = str(d)
                # If already in YYYY-MM or YYYY-MM-DD, try to format month name
                parts = s.split('-')
                if len(parts) >= 2:
                    yyyy = parts[0]
                    mm = parts[1]
                    try:
                        import calendar
                        mname = calendar.month_abbr[int(mm)]
                        return f"{mname} {yyyy}"
                    except Exception:
                        return s
                # fallback: return raw
                return s

            s_s = fmt(start)
            s_e = fmt(end) if end is not None else None
            if s_s and s_e:
                disp = f"{s_s} - {s_e}"
            elif s_s and (s_e is None):
                disp = f"{s_s} - Present"
            elif s_s:
                disp = s_s
            else:
                disp = ''
        elif legacy:
            disp = sanitize_value(legacy)

        sanitized['roles'].append({
            'role': sanitize_value(r.get('role')),
            'company': sanitize_value(r.get('company')),
            'start': sanitize_value(start),
            'end': sanitize_value(end),
            'dates': sanitize_value(disp),
            'location': sanitize_value(r.get('location')),
            'done': sanitize_value(r.get('done')),
            'stack': sanitize_value(r.get('stack')),
        })
    return sanitized


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
