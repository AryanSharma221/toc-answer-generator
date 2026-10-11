import unittest
from solvers.dfa_minimizer import DFAMinimizer

class TestHopcroftDFA(unittest.TestCase):
    def test_a_five_state(self):
        states = ["A", "B", "C", "D", "E"]
        alphabet = ["0", "1"]
        transitions = {
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "D"},
            "C": {"0": "C", "1": "E"},
            "D": {"0": "D", "1": "D"},
            "E": {"0": "E", "1": "E"}
        }
        start_state = "A"
        accepting_states = ["D", "E"]
        
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state, accepting_states)
        result = minimizer.minimize()
        
        # Verify state count and groups
        self.assertEqual(len(result['states']), 3)
        self.assertIn("{A,B}", result['states'])
        self.assertIn("C", result['states'])
        self.assertIn("{D,E}", result['states'])

    def test_b_unreachable_accepting(self):
        states = ["A", "B", "C", "D", "E", "F"]
        alphabet = ["0", "1"]
        transitions = {
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "D"},
            "C": {"0": "D", "1": "A"},
            "D": {"0": "C", "1": "B"},
            "E": {"0": "E", "1": "F"},
            "F": {"0": "F", "1": "E"}
        }
        start_state = "A"
        accepting_states = ["E", "F"]
        
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state, accepting_states)
        result = minimizer.minimize()
        
        # Verify reachable states only and correct group
        self.assertEqual(len(result['states']), 1)
        self.assertIn("{A,B,C,D}", result['states'])
        self.assertEqual(len(result['accepting_states']), 0)

if __name__ == '__main__':
    unittest.main()
