from fpdf import FPDF
import json
import os

import yaml

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        title = 'Illia Karpenkov - Full-Stack Developer, Team Lead, Architect'
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        self.cell(w, 10, title, 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 6, "Email: illia.karpenkov@gmail.com | Mobile: +1 778.9177.256 | Vancouver, BC", 0, 1, 'C')
        self.ln(10)

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
yaml_path = os.path.join(here, 'jobs.yaml')
json_path = os.path.join(here, 'jobs.json')
if os.path.exists(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as yf:
        jobs = yaml.safe_load(yf)
else:
    raise FileNotFoundError('jobs.yaml was found in the repository root.')

def safe_text(text):
    return text.replace("–", "-").replace("—", "-").replace("’", "'")

# Generate PDF
pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

for job in jobs:
    clean_body = safe_text(job['body'])
    pdf.add_job_entry(safe_text(job['role']), safe_text(job['company']), safe_text(job['dates']), safe_text(job['location']), clean_body)

pdf.output("Resume3.pdf")
print("PDF generated successfully.")
