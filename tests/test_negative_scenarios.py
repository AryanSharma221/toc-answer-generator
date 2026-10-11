import unittest
from unittest.mock import patch
import graphviz
from core.universal_generator import solve_universal
from solvers.dfa_simulator import DFASimulator
from solvers.dfa_minimizer import DFAMinimizer
from diagrams.dfa_renderer import render_dfa_diagram

class TestNegativeScenarios(unittest.TestCase):
    def test_empty_alphabet_dfa(self):
        data = {
            "states": ["A"],
            "alphabet": [],
            "start_state": "A",
            "accepting_states": ["A"],
            "transitions": {"A": {}}
        }
        res = solve_universal("String Acceptance Traces", data)
        self.assertIn("Alphabet cannot be empty.", res['subquestions'][0]['answer'])

    def test_undefined_dfa_states(self):
        data = {
            "states": ["A"],
            "alphabet": ["0"],
            "start_state": "A",
            "accepting_states": ["B"], # B is undefined!
            "transitions": {"A": {"0": "A"}}
        }
        res = solve_universal("String Acceptance Traces", data)
        self.assertIn("Accepting state 'B' is not in states.", res['subquestions'][0]['answer'])

    def test_missing_dfa_transitions(self):
        data = {
            "states": ["A", "B"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {
                "A": {"0": "B"}, # missing 1
                "B": {"0": "A", "1": "B"}
            }
        }
        res = solve_universal("String Acceptance Traces", data)
        self.assertIn("Missing transition for state 'A' on symbol '1'", res['subquestions'][0]['answer'])

    def test_invalid_regular_expressions(self):
        data = {
            "regex": "(0|1**", # syntax error
            "alphabet": ["0", "1"]
        }
        res = solve_universal("String Acceptance Traces", data)
        self.assertIn("Regex Parsing Error", res['subquestions'][0]['answer'])

    def test_malformed_cfg_productions(self):
        # Empty grammar
        data = {
            "grammar": "",
            "start_symbol": "S",
            "input_tokens": ["a"]
        }
        res = solve_universal("CFG Derivation", data)
        self.assertIn("No productions found", res['subquestions'][0]['answer'])

    def test_undefined_grammar_symbols(self):
        data = {
            "grammar": "S -> aA", # A is undefined
            "start_symbol": "S",
            "input_tokens": ["a"]
        }
        res = solve_universal("CFG Derivation", data)
        ans = res['subquestions'][0]['answer']
        self.assertTrue("Grammar does not cover" in ans or "is not generated" in ans)

    def test_invalid_target_strings(self):
        # Target string has symbol not in alphabet
        data = {
            "states": ["A"],
            "alphabet": ["0"],
            "start_state": "A",
            "accepting_states": ["A"],
            "transitions": {"A": {"0": "A"}},
            "strings": ["0", "1"] # 1 is invalid
        }
        res = solve_universal("String Acceptance Traces", data)
        ans = res['subquestions'][0]['answer']
        self.assertIn("Symbol '1' not in alphabet.", ans)

    @patch('diagrams.dfa_renderer.graphviz.Digraph.render')
    def test_missing_graphviz(self, mock_render):
        # Simulate missing Graphviz executable
        mock_render.side_effect = graphviz.backend.execute.ExecutableNotFound(['dot'])
        
        with self.assertRaisesRegex(RuntimeError, "Graphviz is not installed or not found on PATH"):
            render_dfa_diagram({
                'states': ['A'],
                'alphabet': ['0'],
                'transitions': {'A': {'0': 'A'}},
                'start_state': 'A',
                'accepting_states': []
            }, filename='test')

if __name__ == '__main__':
    unittest.main()
