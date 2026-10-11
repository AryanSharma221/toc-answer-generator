import unittest
from solvers.dfa_minimizer import DFAMinimizer

class TestDFAValidationReachability(unittest.TestCase):
    def test_all_states_reachable(self):
        minimizer = DFAMinimizer(
            states=["A", "B"], alphabet=["0", "1"],
            transitions={"A": {"0": "B", "1": "A"}, "B": {"0": "A", "1": "B"}},
            start_state="A", accepting_states=["B"]
        )
        self.assertIsNone(minimizer.validate())
        res = minimizer.minimize()
        self.assertEqual(len(res['states']), 2)

    def test_unreachable_non_accepting(self):
        minimizer = DFAMinimizer(
            states=["A", "B", "C"], alphabet=["0", "1"],
            transitions={
                "A": {"0": "B", "1": "A"},
                "B": {"0": "A", "1": "B"},
                "C": {"0": "C", "1": "C"} # C is unreachable
            },
            start_state="A", accepting_states=["B"]
        )
        self.assertIsNone(minimizer.validate())
        res = minimizer.minimize()
        # Should drop C
        self.assertNotIn("C", res['states'])
        self.assertEqual(len(res['states']), 2)

    def test_unreachable_accepting(self):
        minimizer = DFAMinimizer(
            states=["A", "B", "C"], alphabet=["0", "1"],
            transitions={
                "A": {"0": "B", "1": "A"},
                "B": {"0": "A", "1": "B"},
                "C": {"0": "C", "1": "C"} # C is unreachable and accepting
            },
            start_state="A", accepting_states=["C"]
        )
        self.assertIsNone(minimizer.validate())
        res = minimizer.minimize()
        self.assertEqual(len(res['accepting_states']), 0)
        self.assertNotIn("C", res['states'])

    def test_invalid_start_state(self):
        minimizer = DFAMinimizer(
            states=["A", "B"], alphabet=["0"],
            transitions={"A": {"0": "B"}, "B": {"0": "A"}},
            start_state="C", accepting_states=[]
        )
        self.assertEqual(minimizer.validate(), "Start state 'C' is not in states.")

    def test_undefined_destination(self):
        minimizer = DFAMinimizer(
            states=["A", "B"], alphabet=["0"],
            transitions={"A": {"0": "C"}, "B": {"0": "A"}},
            start_state="A", accepting_states=[]
        )
        self.assertEqual(minimizer.validate(), "Transition from 'A' on '0' leads to unknown state 'C'.")

    def test_missing_transition(self):
        minimizer = DFAMinimizer(
            states=["A", "B"], alphabet=["0", "1"],
            transitions={"A": {"0": "B"}, "B": {"0": "A", "1": "B"}},
            start_state="A", accepting_states=[]
        )
        self.assertEqual(minimizer.validate(), "Missing transition for state 'A' on symbol '1'.")

    def test_invalid_transition_symbol(self):
        minimizer = DFAMinimizer(
            states=["A", "B"], alphabet=["0", "1"],
            transitions={"A": {"0": "B", "1": "A", "2": "A"}, "B": {"0": "A", "1": "B"}},
            start_state="A", accepting_states=[]
        )
        self.assertEqual(minimizer.validate(), "Invalid transition symbol '2' for state 'A'.")

    def test_duplicate_states(self):
        minimizer = DFAMinimizer(
            states=["A", "A", "B"], alphabet=["0"],
            transitions={"A": {"0": "B"}, "B": {"0": "A"}},
            start_state="A", accepting_states=[]
        )
        self.assertEqual(minimizer.validate(), "Duplicate states found.")

if __name__ == '__main__':
    unittest.main()
