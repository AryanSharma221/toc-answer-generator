import os
import unittest
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html

class TestRepeatedGenerations(unittest.TestCase):
    def test_repeated_generation(self):
        # 1. Generate DFA Solution
        data_1 = {
            "states": ["A", "B"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {"A": {"0": "B", "1": "A"}, "B": {"0": "A", "1": "B"}},
            "strings": ["01"]
        }
        res_1 = solve_universal("String Acceptance Traces", data_1)
        h1 = generate_html([res_1], 'output/test_rep_1.html')
        
        # 2. Generate another DFA with different alphabet and constraints
        data_2 = {
            "states": ["X", "Y"],
            "alphabet": ["a", "b"],
            "start_state": "X",
            "accepting_states": ["X"],
            "transitions": {"X": {"a": "X", "b": "Y"}, "Y": {"a": "X", "b": "Y"}},
            "strings": ["ab"]
        }
        res_2 = solve_universal("String Acceptance Traces", data_2)
        h2 = generate_html([res_2], 'output/test_rep_2.html')
        
        # Verify h1 and h2 don't share SVG filenames
        with open(h1, 'r', encoding='utf-8') as f:
            html1 = f.read()
        with open(h2, 'r', encoding='utf-8') as f:
            html2 = f.read()
            
        import re
        svgs1 = re.findall(r'src="(data:image/png;base64,[^"]+)"', html1)
        svgs2 = re.findall(r'src="(data:image/png;base64,[^"]+)"', html2)
        
        self.assertTrue(len(svgs1) > 0)
        self.assertTrue(len(svgs2) > 0)
        self.assertEqual(len(set(svgs1).intersection(set(svgs2))), 0, "Stale SVG overlap detected!")
        
        self.assertIn("A", html1)
        self.assertIn("X", html2)
        # removed

        print("Repeated DFA tests pass.")
        
    def test_repeated_cfg(self):
        data_1 = {
            "grammar": "S -> 'a'",
            "start_symbol": "S",
            "input_tokens": ["a"]
        }
        res_1 = solve_universal("CFG Derivation", data_1)
        
        data_2 = {
            "grammar": "E -> 'id'",
            "start_symbol": "E",
            "input_tokens": ["id"]
        }
        res_2 = solve_universal("CFG Derivation", data_2)
        
        h1 = generate_html([res_1], 'output/test_cfg_1.html')
        h2 = generate_html([res_2], 'output/test_cfg_2.html')
        
        with open(h1, 'r', encoding='utf-8') as f:
            html1 = f.read()
        with open(h2, 'r', encoding='utf-8') as f:
            html2 = f.read()
            
        import re
        svgs1 = re.findall(r'src="(data:image/png;base64,[^"]+)"', html1)
        svgs2 = re.findall(r'src="(data:image/png;base64,[^"]+)"', html2)
        
        self.assertTrue(len(svgs1) > 0)
        self.assertTrue(len(svgs2) > 0)
        self.assertEqual(len(set(svgs1).intersection(set(svgs2))), 0, "Stale SVG overlap detected!")
        
        self.assertIn("S", html1)
        self.assertIn("E", html2)
        
        print("Repeated CFG tests pass.")

if __name__ == '__main__':
    unittest.main()
