from fpdf import FPDF
import json
import os

import yaml

class PDF(FPDF):
    def header(self):
        # Render resume header (name/title and contact) if header_data is provided
        # Only render on the first page
        if getattr(self, 'page_no', lambda: 0)() > 1:
            return
        header = getattr(self, 'header_data', {}) or {}
        title = header.get('title', '')
        contact = header.get('contact', '')
        if not title and not contact:
            return
        # Title
        self.set_font('Arial', 'B', 16)
        # move to top with a small margin
        self.set_y(10)
        self.cell(0, 8, safe_text(title), ln=1, align='C')
        # Contact info
        self.set_font('Arial', '', 10)
        self.cell(0, 6, safe_text(contact), ln=1, align='C')
        # Draw a separating line
        self.ln(2)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
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

    def add_job_entry(self, role, company, dates, location, body):
        title_font = ('Arial', 'B', 12)
        sub_font = ('Arial', 'I', 10)
        body_font = ('Arial', '', 10)
        full_width = 190
        h_title = 6
        h_sub = 6
        h_gap = 5
        h_body = self.get_lines_height(full_width, body, body_font[0], body_font[1], body_font[2], 5)
        total_needed_height = h_title + h_sub + h_body + h_gap
        page_height = 297
        bottom_margin_buffer = 20
        current_y = self.get_y()
        if total_needed_height > page_height - current_y - bottom_margin_buffer:
            self.add_page()
        self.set_font(*title_font)
        self.cell(0, 6, f"{role}", 0, 1, 'L')
        self.set_font(*sub_font)
        self.cell(0, 6, f"{company} | {dates} | {location}", 0, 1, 'L')
        self.set_font(*body_font)
        self.multi_cell(0, 5, body)
        self.ln(h_gap)

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
    raise FileNotFoundError('jobs.yaml was found in the repository root.')

def safe_text(text):
    return text.replace("–", "-").replace("—", "-").replace("’", "'")

# Generate PDF
pdf = PDF()
pdf.header_data = header
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
for role in roles:
    pdf.add_job_entry(
        safe_text(role['role']), 
        safe_text(role['company']), 
        safe_text(role['dates']), 
        safe_text(role['location']), 
        safe_text(role['body']))

pdf.output("Resume Illia Karpenkov.pdf")
print("PDF generated successfully.")
