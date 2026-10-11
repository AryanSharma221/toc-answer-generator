import os
import unittest
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html

class TestHTMLExporter(unittest.TestCase):
    def test_mode_b_export(self):
        # 1. CFG Data
        data_cfg = {
            "grammar": "E -> E '+' E | E '*' E | 'id'",
            "start_symbol": "E",
            "input_tokens": ["id", "+", "id", "*", "id"]
        }
        res_cfg = solve_universal("CFG Derivation", data_cfg)
        
        # 2. Regex Data
        data_regex = {
            "regex": "(0|1)*01",
            "alphabet": ["0", "1"],
            "strings": ["01"]
        }
        res_regex = solve_universal("String Acceptance Traces", data_regex)
        
        # 3. Export
        report_data = [res_cfg, res_regex]
        output_file = generate_html(report_data, 'output/test_report.html')
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Verify CFG
        self.assertIn("Parsed Grammar", html) # Specification
        self.assertIn("&rArr; id + id * id", html) # Derivations
        self.assertIn("data:image/png;base64", html) # Unique UUID diagrams now embedded as base64
        self.assertIn("Parse Tree", html) # Captions
        self.assertIn("Ambiguity Structural Difference", html) # Intermediate reasoning / conclusions
        
        # Verify Regex
        self.assertIn("Regex Conversion Pipeline", html)
        self.assertIn("Expression: <strong>(0|1)*01</strong>", html) # User spec
        self.assertIn("Accepted", html) # Conclusion
        
        print("Export test passed and validated against deliverables.")

if __name__ == '__main__':
    unittest.main()
