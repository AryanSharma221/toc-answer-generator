import unittest
from core.universal_generator import solve_universal

class TestDFAMinimizationIndependent(unittest.TestCase):
    def test_minimization_ui_output(self):
        data = {
            "states": ["A", "B", "C", "D", "E"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B", "C"],
            "transitions": {
                "A": {"0": "B", "1": "C"},
                "B": {"0": "D", "1": "D"},
                "C": {"0": "D", "1": "D"},
                "D": {"0": "D", "1": "D"},
                "E": {"0": "E", "1": "E"}
            }
        }
        res = solve_universal("DFA Minimization", data)
        html = res['subquestions'][0]['answer']
        self.assertIn("Minimized DFA Transition Table", html)
        self.assertIn("{B,C}", html)

if __name__ == '__main__':
    unittest.main()
