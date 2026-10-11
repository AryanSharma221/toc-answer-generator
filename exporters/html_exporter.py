import os
import base64
import re

def generate_html(report_data, output_file='output/report.html'):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset=\"UTF-8\">",
        "<title>Theory of Computation Answer Generator</title>",
        "<style>",
        ":root {",
        "  --bg-primary: #ffffff;",
        "  --bg-card: #f8fafc;",
        "  --bg-code: #f1f5f9;",
        "  --text-primary: #0f172a;",
        "  --text-secondary: #334155;",
        "  --text-muted: #64748b;",
        "  --border-color: #cbd5e1;",
        "  --border-light: #e2e8f0;",
        "  --accent-color: #2563eb;",
        "  --table-header-bg: #f1f5f9;",
        "  --table-stripe-bg: #f8fafc;",
        "  --badge-success-bg: #dcfce7;",
        "  --badge-success-text: #166534;",
        "  --badge-success-border: #86efac;",
        "  --badge-danger-bg: #fee2e2;",
        "  --badge-danger-text: #991b1b;",
        "  --badge-danger-border: #fca5a5;",
        "  --badge-warning-bg: #fef3c7;",
        "  --badge-warning-text: #92400e;",
        "  --badge-warning-border: #fcd34d;",
        "}",
        "@media (prefers-color-scheme: dark) {",
        "  :root {",
        "    --bg-primary: #0f172a;",
        "    --bg-card: #1e293b;",
        "    --bg-code: #1e293b;",
        "    --text-primary: #f8fafc;",
        "    --text-secondary: #cbd5e1;",
        "    --text-muted: #94a3b8;",
        "    --border-color: #334155;",
        "    --border-light: #475569;",
        "    --accent-color: #3b82f6;",
        "    --table-header-bg: #1e293b;",
        "    --table-stripe-bg: #1e293b;",
        "    --badge-success-bg: #14532d;",
        "    --badge-success-text: #bbf7d0;",
        "    --badge-success-border: #22c55e;",
        "    --badge-danger-bg: #7f1d1d;",
        "    --badge-danger-text: #fecaca;",
        "    --badge-danger-border: #ef4444;",
        "    --badge-warning-bg: #78350f;",
        "    --badge-warning-text: #fde68a;",
        "    --badge-warning-border: #f59e0b;",
        "  }",
        "}",
        "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: var(--text-primary); background-color: var(--bg-primary); line-height: 1.6; }",
        "h1 { color: var(--text-primary); }",
        "h2 { color: var(--text-secondary); margin-top: 30px; border-bottom: 2px solid var(--border-light); padding-bottom: 10px; }",
        "h3 { color: var(--accent-color); }",
        "p { margin: 10px 0; color: var(--text-primary); }",
        "figure { margin: 20px 0; text-align: center; page-break-inside: avoid; }",
        "table { border-collapse: collapse; page-break-inside: avoid; margin: 20px 0; width: 100%; border: 1px solid var(--border-color); background-color: var(--bg-primary); color: var(--text-primary); }",
        "th { background-color: var(--table-header-bg); color: var(--text-primary); font-weight: 600; padding: 10px; border: 1px solid var(--border-color); }",
        "td { padding: 8px 10px; border: 1px solid var(--border-color); color: var(--text-primary); }",
        "tbody tr:nth-child(even) { background-color: var(--table-stripe-bg); }",
        "pre, code { font-family: 'Consolas', 'Courier New', monospace; }",
        "code { background-color: var(--bg-code); color: var(--text-primary); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-light); }",
        "pre { background-color: var(--bg-code); color: var(--text-primary); padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); overflow-x: auto; }",
        "img { max-width: 100%; height: auto; }",
        "figcaption { font-style: italic; color: var(--text-muted); margin-top: 10px; }",
        ".question { font-weight: bold; background-color: var(--bg-card); color: var(--text-primary); padding: 10px; border-left: 4px solid var(--accent-color); }",
        ".answer { margin-bottom: 40px; color: var(--text-primary); }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Theory of Computation Answer Report</h1>"
    ]
    
    def replace_with_b64(match):
        img_path = match.group(1)
        # Handle relative or absolute paths, normalize them
        if not os.path.exists(img_path):
            # Sometimes it's passed as output/figures/... 
            if os.path.exists(os.path.join(os.getcwd(), img_path)):
                img_path = os.path.join(os.getcwd(), img_path)
            else:
                return match.group(0) # Leave as is if file not found
        
        try:
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            mime = "image/svg+xml" if img_path.endswith('.svg') else "image/png"
            return f'src="data:{mime};base64,{encoded_string}"'
        except Exception:
            return match.group(0)

    for question_data in report_data:
        html_content.append(f"<h2>{question_data['title']}</h2>")
        if 'preamble' in question_data:
            html_content.append(f"<div class=\"preamble\">{question_data['preamble']}</div>")
        for subq in question_data['subquestions']:
            html_content.append(f"<div class=\"question\">{subq['question']}</div>")
            html_content.append(f"<div class=\"answer\">")
            
            # Embed all images as base64 to ensure they render in Streamlit and standalone downloaded HTML files
            answer_html = re.sub(r'src="([^"]+)"', replace_with_b64, subq['answer'])
            html_content.append(answer_html)
            
            html_content.append("</div>")
            
    html_content.append("</body>")
    html_content.append("</html>")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    return output_file
