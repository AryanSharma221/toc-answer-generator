import unittest
from solvers.dfa_simulator import DFASimulator

class TestDFARegression(unittest.TestCase):
    def setUp(self):
        # Language: binary strings ending in 1
        states = ["A", "B"]
        alphabet = ["0", "1"]
        start_state = "A"
        accepting_states = ["B"]
        transitions = {
            "A": {"0": "A", "1": "B"},
            "B": {"0": "A", "1": "B"}
        }
        self.dfa = DFASimulator(states, alphabet, transitions, start_state, accepting_states)

    def test_dfa_regression_strings(self):
        # Expected results as tuples: (string, expected_acceptance)
        test_cases = [
            ("1", True),
            ("01", True),
            ("001", True),
            ("0001", True),
            ("", False),
            ("0", False),
            ("10", False),
            ("101", True),
        ]
        
        for s, expected in test_cases:
            with self.subTest(string=s):
                result = self.dfa.simulate(s)
                self.assertEqual(result["accepted"], expected, f"Failed on string '{s}'")
                
    def test_malformed_input(self):
        # Missing state transition
        bad_transitions = {
            "A": {"0": "A"}, # Missing '1'
            "B": {"0": "A", "1": "B"}
        }
        bad_dfa = DFASimulator(["A", "B"], ["0", "1"], bad_transitions, "A", ["B"])
        val_error = bad_dfa.validate()
        self.assertIsNotNone(val_error)
        self.assertIn("Missing transition", val_error)

if __name__ == '__main__':
    unittest.main()
