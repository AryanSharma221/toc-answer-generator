import unittest
from solvers.dfa_minimizer import DFAMinimizer

class TestDFAMinimizer(unittest.TestCase):
    def test_three_state_minimization(self):
        # We use the intended DFA that correctly minimizes to 3 states.
        # (Assuming B->1 is C, which groups A and B).
        states = ["A", "B", "C", "D", "E"]
        alphabet = ["0", "1"]
        transitions = {
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "C"},
            "C": {"0": "C", "1": "E"},
            "D": {"0": "D", "1": "D"},
            "E": {"0": "E", "1": "E"}
        }
        start_state = "A"
        accepting_states = ["D", "E"]
        
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state, accepting_states)
        result = minimizer.minimize()
        
        # After removing unreachable states (D), we get 3 states.
        self.assertEqual(len(result['states']), 3)
        self.assertIn("{A,B}", result['states'])
        self.assertIn("C", result['states'])
        self.assertIn("E", result['states'])
        
        # Check transitions
        self.assertEqual(result['transitions']["{A,B}"]["0"], "{A,B}")
        self.assertEqual(result['transitions']["{A,B}"]["1"], "C")
        
        self.assertEqual(result['transitions']["C"]["0"], "C")
        self.assertEqual(result['transitions']["C"]["1"], "E")
        
        self.assertEqual(result['transitions']["E"]["0"], "E")
        self.assertEqual(result['transitions']["E"]["1"], "E")

if __name__ == '__main__':
    unittest.main()
