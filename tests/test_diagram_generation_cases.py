import unittest
import os
import shutil
from core.universal_generator import solve_universal

class TestDiagramGenerationCases(unittest.TestCase):
    def test_case_a(self):
        # Five-state DFA
        data = {
            "states": ["A", "B", "C", "D", "E"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["D", "E"],
            "transitions": {
                "A": {"0": "B", "1": "C"},
                "B": {"0": "A", "1": "D"},
                "C": {"0": "C", "1": "E"},
                "D": {"0": "D", "1": "D"},
                "E": {"0": "E", "1": "E"}
            },
            "strings": []
        }
        
        out = solve_universal("DFA Minimization", data)
        html_out = out['subquestions'][0]['answer']
        
        self.assertIn("<li>{A,B}</li>", html_out)
        self.assertIn("<li>{D,E}</li>", html_out)
        self.assertIn("mode_b_min_dfa_", html_out)
        
    def test_case_b(self):
        # Six-state DFA
        data = {
            "states": ["A", "B", "C", "D", "E", "F"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["E", "F"],
            "transitions": {
                "A": {"0": "B", "1": "C"},
                "B": {"0": "A", "1": "D"},
                "C": {"0": "D", "1": "A"},
                "D": {"0": "C", "1": "B"},
                "E": {"0": "E", "1": "F"},
                "F": {"0": "F", "1": "E"}
            },
            "strings": []
        }
        
        out = solve_universal("DFA Minimization", data)
        html_out = out['subquestions'][0]['answer']
        self.assertIn("<li>{A,B,C,D}</li>", html_out)
        self.assertIn("mode_b_min_dfa_", html_out)

    def test_case_c(self):
        # Binary strings ending in 1
        data = {
            "states": ["A", "B"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {
                "A": {"0": "A", "1": "B"},
                "B": {"0": "A", "1": "B"}
            },
            "strings": []
        }
        
        out = solve_universal("DFA Minimization", data)
        html_out = out['subquestions'][0]['answer']
        self.assertIn("<li>A</li>", html_out)
        self.assertIn("<li>B</li>", html_out)
        self.assertIn("mode_b_min_dfa_", html_out)

if __name__ == '__main__':
    unittest.main()
