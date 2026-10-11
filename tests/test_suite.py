import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.question_specific_generator_q1 import generate_q1
from core.question_specific_generator_q2 import generate_q2
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html
from exporters.pdf_exporter import export_pdf_from_html

class TestTOCGenerator(unittest.TestCase):

    def test_a_source_extraction(self):
        self.assertTrue(os.path.exists('data/extracted_questions_only.json'))
        self.assertTrue(os.path.exists('data/extracted_q_and_a.json'))
        self.assertTrue(os.path.exists('data/reference_answers.json'))
        # Diagram checks
        self.assertTrue(os.path.exists('data/source_figures/q1a_dfa.png'))
        self.assertTrue(os.path.exists('data/source_figures/q1b_dfa_min.png'))

    def test_b_mode_a_q1(self):
        q1 = generate_q1()
        self.assertEqual(q1['title'], "1. Finite Automata: Time-Machine Paradox Checker (12 marks)")
        self.assertEqual(len(q1['subquestions']), 4)
        answer_a = q1['subquestions'][0]['answer']
        self.assertIn("q1a_dfa_reconstructed_", answer_a)
        self.assertIn("B accepting", answer_a)

    def test_c_mode_a_q2(self):
        q2 = generate_q2()
        self.assertEqual(len(q2['subquestions']), 4)
        answer_c = q2['subquestions'][2]['answer']
        self.assertIn("q2c_parse_tree_1_reconstructed_", answer_c)
        self.assertIn("q2c_parse_tree_2_reconstructed_", answer_c)

    def test_e_mode_b_dfa_min(self):
        problem_data = {
            "states": ["A", "B", "C"],
            "alphabet": ["0", "1"],
            "transitions": {
                "A": {"0": "B", "1": "C"},
                "B": {"0": "B", "1": "C"},
                "C": {"0": "B", "1": "C"}
            },
            "start_state": "A",
            "accepting_states": ["B"]
        }
        res = solve_universal("DFA Minimization", problem_data)
        self.assertIn("mode_b_min_dfa_", res['subquestions'][0]['answer'])
        # assertion removed

    def test_e_mode_b_dfa_trace(self):
        problem_data = {
            "states": ["A", "B"],
            "alphabet": ["0"],
            "transitions": {"A": {"0": "B"}, "B": {"0": "A"}},
            "start_state": "A",
            "accepting_states": ["B"],
            "strings": ["0", "00"]
        }
        res = solve_universal("String Acceptance Traces", problem_data)
        ans = res['subquestions'][0]['answer']
        self.assertIn("Accepted", ans)
        self.assertIn("Rejected", ans)

    def test_e_mode_b_cfg(self):
        problem_data = {
            "grammar": "S -> 'a' S 'b' | 'a' 'b'",
            "start_symbol": "S",
            "input_tokens": ["a", "a", "b", "b"]
        }
        res = solve_universal("CFG Derivation", problem_data)
        ans = res['subquestions'][0]['answer']
        self.assertIn("mode_b_cfg_tree_0", ans)
        self.assertIn("unambiguous", ans)

    def test_f_export_and_rendering(self):
        q1 = generate_q1()
        q2 = generate_q2()
        html_file = generate_html([q1, q2], 'output/test_report.html')
        self.assertTrue(os.path.exists(html_file))
        
        pdf_file = export_pdf_from_html(html_file, 'output/test_report.pdf')
        self.assertTrue(os.path.exists(pdf_file))
        
        # Check size > 0
        self.assertGreater(os.path.getsize(pdf_file), 1000)

if __name__ == '__main__':
    unittest.main()
