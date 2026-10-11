import unittest
import os
import json
from exporters.html_exporter import generate_html
from exporters.pdf_exporter import export_pdf_from_html
from solvers.dfa_minimizer import DFAMinimizer
from diagrams.dfa_renderer import render_dfa_diagram
from core.universal_generator import solve_dfa_minimization

class TestExportPipeline(unittest.TestCase):
    def test_export_diagram_embedding(self):
        # 1. Provide minimal DFA
        problem_data = {
          "states": ["A", "B"],
          "start_state": "A",
          "accepting_states": ["B"],
          "transitions": {
            "A": {"0": "A", "1": "B"},
            "B": {"0": "A", "1": "B"}
          },
          "alphabet": ["0", "1"]
        }
        
        # 2. Emulate the universal generator pipeline to get HTML output structure
        res = {
            "title": "DFA Minimization Analysis",
            "preamble": "Testing Exports",
            "subquestions": [{
                "question": "Result",
                "answer": "<img src=\"output/figures/dummy.png\" />"
            }]
        }
        
        # We need to actually generate the image to test Base64 injection
        minimized = DFAMinimizer(**problem_data).minimize()
        img_path = render_dfa_diagram(minimized, filename='test_export_img')
        
        res['subquestions'][0]['answer'] = f"<img src=\"{img_path}\" />"
        
        # 3. Generate HTML Report
        html_file = generate_html([res], 'output/test_export_report.html')
        self.assertTrue(os.path.exists(html_file))
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # The local file path MUST have been substituted with Base64
        self.assertNotIn('src="output/figures', html_content)
        self.assertIn('src="data:image/png;base64,', html_content)
        
        # 4. Generate PDF Report
        pdf_file = export_pdf_from_html(html_file)
        self.assertTrue(os.path.exists(pdf_file))
        self.assertGreater(os.path.getsize(pdf_file), 1000) # Ensure it's a valid PDF (not empty)

if __name__ == '__main__':
    unittest.main()
