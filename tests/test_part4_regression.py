import unittest
from solvers.dfa_minimizer import DFAMinimizer
from diagrams.dfa_renderer import render_dfa_diagram

class TestPart4Regression(unittest.TestCase):
    def run_pipeline(self, dfa_input):
        minimizer = DFAMinimizer(
            dfa_input['states'],
            dfa_input['alphabet'],
            dfa_input['transitions'],
            dfa_input['start_state'],
            dfa_input['accepting_states']
        )
        self.assertIsNone(minimizer.validate())
        
        # 1. Receive the verified minimized-DFA object
        minimized = minimizer.minimize()
        
        # 2. Generate its state diagram automatically
        output_path = render_dfa_diagram(minimized, filename='test_pipeline')
        
        return minimized, output_path

    def test_case_a_five_state_dfa(self):
        dfa = {
          "states": ["A", "B", "C", "D", "E"],
          "start_state": "A",
          "accepting_states": ["D", "E"],
          "transitions": {
            "A": {"0": "B", "1": "C"},
            "B": {"0": "A", "1": "D"},
            "C": {"0": "C", "1": "E"},
            "D": {"0": "D", "1": "D"},
            "E": {"0": "E", "1": "E"}
          },
          "alphabet": ["0", "1"]
        }
        
        minimized, output_path = self.run_pipeline(dfa)
        
        # Expected partition: {A,B}, {C}, {D,E}
        states = minimized['states']
        self.assertEqual(len(states), 3)
        self.assertIn('{A,B}', states)
        self.assertIn('C', states)
        self.assertIn('{D,E}', states)
        
        # Transitions
        self.assertEqual(minimized['transitions']['{A,B}']['0'], '{A,B}')
        self.assertEqual(minimized['transitions']['{A,B}']['1'], 'C')
        self.assertEqual(minimized['transitions']['C']['1'], '{D,E}')
        
        # Accepting
        self.assertEqual(minimized['accepting_states'], ['{D,E}'])
        self.assertEqual(minimized['start_state'], '{A,B}')

    def test_case_b_six_state_dfa(self):
        dfa = {
          "states": ["A", "B", "C", "D", "E", "F"],
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
          "alphabet": ["0", "1"]
        }
        
        minimized, output_path = self.run_pipeline(dfa)
        
        # Expected reachable states: A, B, C, D
        # Expected minimized partition: {A,B,C,D}
        states = minimized['states']
        self.assertEqual(len(states), 1)
        self.assertIn('{A,B,C,D}', states)
        
        # Expected diagram: exactly one non-accepting state with self-loops on 0 and 1.
        self.assertEqual(minimized['accepting_states'], [])
        self.assertEqual(minimized['transitions']['{A,B,C,D}']['0'], '{A,B,C,D}')
        self.assertEqual(minimized['transitions']['{A,B,C,D}']['1'], '{A,B,C,D}')

    def test_case_c_binary_ends_in_1(self):
        dfa = {
          "states": ["A", "B"],
          "start_state": "A",
          "accepting_states": ["B"],
          "transitions": {
            "A": {"0": "A", "1": "B"},
            "B": {"0": "A", "1": "B"}
          },
          "alphabet": ["0", "1"]
        }
        
        minimized, output_path = self.run_pipeline(dfa)
        
        # Expected minimized state count: two.
        states = minimized['states']
        self.assertEqual(len(states), 2)
        
        self.assertIn('A', states)
        self.assertIn('B', states)
        self.assertEqual(minimized['accepting_states'], ['B'])
        self.assertEqual(minimized['transitions']['A']['1'], 'B')

if __name__ == '__main__':
    unittest.main()
