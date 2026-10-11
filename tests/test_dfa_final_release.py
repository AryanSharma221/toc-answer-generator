import unittest
from solvers.dfa_minimizer import DFAMinimizer
from solvers.dfa_verification import moore_minimize, table_filling_minimize, verify_quotient, verify_language_equivalence

class TestDFAFinalRelease(unittest.TestCase):
    def test_case_4_already_minimal(self):
        # A DFA that is already minimal (Odd number of 1s)
        states = ["E", "O"]
        alphabet = ["0", "1"]
        transitions = {
            "E": {"0": "E", "1": "O"},
            "O": {"0": "O", "1": "E"}
        }
        start_state = "E"
        accepting_states = ["O"]
        
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state, accepting_states)
        res = minimizer.minimize()
        
        self.assertEqual(len(res['states']), 2)

    def test_case_5_all_reachable_accepting(self):
        states = ["A", "B", "C"]
        alphabet = ["0", "1"]
        transitions = {
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "C"},
            "C": {"0": "C", "1": "C"}
        }
        start_state = "A"
        accepting_states = ["A", "B", "C"]
        
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state, accepting_states)
        res = minimizer.minimize()
        
        self.assertEqual(len(res['states']), 1)

if __name__ == '__main__':
    unittest.main()
