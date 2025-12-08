from fpdf import FPDF
import json
import os

import yaml

class PDF(FPDF):
    def header(self):
        # Render resume header (name/title and contact) if header_data is provided
        # Only render on the first page
        # Only print header on the first page
        if self.page_no() > 1:
            return
        header = getattr(self, 'header_data', {}) or {}
        title = header.get('title', '')
        contact = header.get('contact', '')
        if not title and not contact:
            return
        # Attempt to split name and tagline from title if present
        name = title
        tagline = ''
        if ' - ' in title:
            parts = title.split(' - ', 1)
            name = parts[0].strip()
            tagline = parts[1].strip()

        # move to top with a slightly larger top margin
        self.set_y(12)
        # Name
        self.set_font('Arial', 'B', 18)
        self.cell(0, 8, safe_text(name), ln=1, align='C')
        # Tagline
        if tagline:
            self.set_font('Arial', '', 11)
            self.cell(0, 6, safe_text(tagline), ln=1, align='C')
        # Contact info
        if contact:
            self.set_font('Arial', '', 9)
            self.cell(0, 5, safe_text(contact), ln=1, align='C')
        # Draw a subtle separating line
        self.ln(2)
        self.set_draw_color(50, 50, 50)
        self.set_line_width(0.25)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)
    def get_lines_height(self, text_width, text, font_family, font_style, font_size, line_height):
        original_font = (self.font_family, self.font_style, self.font_size_pt)
        self.set_font(font_family, font_style, font_size)
        lines = 0
        for paragraph in text.split('\n'):
            if not paragraph:
                lines += 1
                continue
            words = paragraph.split(' ')
            current_line_width = 0
            lines += 1
            for word in words:
                word_width = self.get_string_width(word + ' ')
                if current_line_width + word_width > text_width:
                    lines += 1
                    current_line_width = word_width
                else:
                    current_line_width += word_width
        self.set_font(original_font[0], original_font[1], original_font[2])
        return lines * line_height

    def add_job_entry(self, role, company, dates, location, done, stack):
        # Fonts and layout
        title_font = ('Arial', 'B', 12)
        dates_font = ('Arial', '', 10)
        sub_font = ('Arial', 'I', 10)
        body_font = ('Arial', '', 10)
        gap_after = 6

        # Calculate available width based on margins
        full_width = self.w - self.l_margin - self.r_margin

        # Simple page break heuristic: if the remaining space is small, start a new page
        if self.get_y() > self.h - self.b_margin - 60:
            self.add_page()

        # Role on the left, dates on the right
        self.set_font(*title_font)
        self.cell(0, 6, f"{role}", 0, 0, 'L')
        self.set_font(*dates_font)
        # Place dates aligned to the right
        self.cell(-self.l_margin, 6, f"{dates}", 0, 1, 'R')

        # Company and location
        self.set_font(*sub_font)
        # use ASCII-friendly separator
        company_line = f"{company} - {location}" if location else company
        self.cell(0, 6, company_line, 0, 1, 'L')

        # Done: support simple bullet rendering for lines starting with '-'
        self.set_font(*body_font)
        for paragraph in done.split('\n'):
            paragraph = paragraph.strip()
            if not paragraph:
                self.ln(2)
                continue
            if paragraph.startswith('-'):
                content = paragraph.lstrip('-').strip()
                # small indent for bullets
                indent = 6
                # bullet symbol (ASCII-friendly to avoid encoding issues)
                bullet = '- '
                # print bullet and wrapped content
                # set x to left margin + indent
                self.set_x(self.l_margin + indent)
                # print the bullet as a small cell
                self.cell(6, 5, bullet, 0, 0)
                # print the rest as a multi-cell with reduced width
                self.multi_cell(full_width - indent - 6, 5, content)
            else:
                # normal paragraph
                self.multi_cell(full_width, 5, paragraph)
        self.ln(2)

        # Stack (technology/tools) - render in a slightly smaller italic font
        if stack:
            self.set_font('Arial', 'I', 9)
            # prefix with 'Stack: ' for clarity
            self.multi_cell(full_width, 5, safe_text(f"Stack: {stack}"))
        self.ln(gap_after)

    def footer(self):
        # Footer with page number
        self.set_y(-12)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.25)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 8, f'Page {self.page_no()}', 0, 0, 'C')

# --- Resume Data ---
here = os.path.dirname(__file__)
yaml_path = os.path.join(here, 'data.yaml')
if os.path.exists(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as yf:
        data = yaml.safe_load(yf)
        # support new format: mapping with header and roles
        if isinstance(data, dict):
            header = data.get('header', {})
            roles = data.get('roles', [])
        else:
            header = {}
            roles = data
else:
    raise FileNotFoundError('data.yaml was not found in the repository root.')

def safe_text(text):
    return text.replace("–", "-").replace("—", "-").replace("’", "'")

# Generate PDF
pdf = PDF()
# sanitize header values to avoid characters not representable in latin-1 used by fpdf
sanitized_header = {}
for k, v in (header or {}).items():
    if v is None:
        sanitized_header[k] = ''
    else:
        sanitized_header[k] = safe_text(str(v))
pdf.header_data = sanitized_header
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
for role in roles:
    pdf.add_job_entry(
        safe_text(role.get('role', '')),
        safe_text(role.get('company', '')),
        safe_text(role.get('dates', '')),
        safe_text(role.get('location', '')),
        safe_text(role.get('done', '')),
        safe_text(role.get('stack', '')))

pdf.output("Resume-Illia-Karpenkov.pdf")
print("PDF generated successfully.")
