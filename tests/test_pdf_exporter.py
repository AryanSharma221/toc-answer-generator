import os
import unittest
import fitz
from core.question_specific_generator_q1 import generate_q1
from core.question_specific_generator_q2 import generate_q2
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html
from exporters.pdf_exporter import export_pdf_from_html

class TestPDFExporter(unittest.TestCase):
    def render_pdf_to_images(self, pdf_path, prefix):
        os.makedirs('output/pdf_pages', exist_ok=True)
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            out_path = f"output/pdf_pages/{prefix}_page_{page_num+1}.png"
            pix.save(out_path)
        return len(doc)

    def test_pdf_exports(self):
        q1_data = generate_q1()
        q2_data = generate_q2()
        
        # 1. Mode A Q1
        h1 = generate_html([q1_data], 'output/test_q1.html')
        p1 = export_pdf_from_html(h1, 'output/test_q1.pdf')
        self.assertTrue(os.path.exists(p1))
        pages1 = self.render_pdf_to_images(p1, 'test_q1')
        self.assertTrue(pages1 > 0)
        
        # 2. Mode A Q2
        h2 = generate_html([q2_data], 'output/test_q2.html')
        p2 = export_pdf_from_html(h2, 'output/test_q2.pdf')
        pages2 = self.render_pdf_to_images(p2, 'test_q2')
        self.assertTrue(pages2 > 0)
        
        # 3. Mode A Q1 + Q2
        h12 = generate_html([q1_data, q2_data], 'output/test_q12.html')
        p12 = export_pdf_from_html(h12, 'output/test_q12.pdf')
        pages12 = self.render_pdf_to_images(p12, 'test_q12')
        self.assertTrue(pages12 > 0)
        
        # 4. Universal DFA problem
        dfa_data = {
            "states": ["A", "B"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {
                "A": {"0": "B", "1": "A"},
                "B": {"0": "A", "1": "B"}
            }
        }
        res_dfa = solve_universal("String Acceptance Traces", dfa_data)
        h_dfa = generate_html([res_dfa], 'output/test_dfa.html')
        p_dfa = export_pdf_from_html(h_dfa, 'output/test_dfa.pdf')
        pages_dfa = self.render_pdf_to_images(p_dfa, 'test_dfa')
        self.assertTrue(pages_dfa > 0)
        
        # 5. Universal CFG derivation
        cfg_data = {
            "grammar": "S -> aSb | epsilon",
            "start_symbol": "S",
            "input_tokens": list("aaabbb")
        }
        res_cfg = solve_universal("CFG Derivation", cfg_data)
        h_cfg = generate_html([res_cfg], 'output/test_cfg.html')
        p_cfg = export_pdf_from_html(h_cfg, 'output/test_cfg.pdf')
        pages_cfg = self.render_pdf_to_images(p_cfg, 'test_cfg')
        self.assertTrue(pages_cfg > 0)

        print("All PDFs successfully exported and rasterized.")

if __name__ == '__main__':
    unittest.main()
