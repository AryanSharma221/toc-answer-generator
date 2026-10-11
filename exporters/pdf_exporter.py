import os
from weasyprint import HTML

def export_pdf_from_html(html_file, output_file='output/report.pdf'):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    # WeasyPrint needs a base_url so it can resolve relative paths (like images).
    base_url = os.path.dirname(os.path.abspath(html_file))
    HTML(filename=html_file, base_url=base_url).write_pdf(output_file)
    return output_file
