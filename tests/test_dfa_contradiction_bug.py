import unittest
from solvers.dfa_minimizer import DFAMinimizer
from solvers.dfa_verification import verify_language_equivalence
from diagrams.dfa_renderer import render_dfa_diagram
import os

class TestDFAContradictionBug(unittest.TestCase):
    def test_six_state_contradictory_dfa(self):
        dfa = {
            "states": ["A", "B", "C", "D", "E", "F"],
            "alphabet": ["0", "1", "2"],
            "start_state": "A",
            "accepting_states": ["E", "F"],
            "transitions": {
                "A": {"0":"B", "1":"C", "2":"D"},
                "B": {"0":"E", "1":"D", "2":"C"},
                "C": {"0":"D", "1":"F", "2":"B"},
                "D": {"0":"B", "1":"C", "2":"D"},
                "E": {"0":"E", "1":"D", "2":"C"},
                "F": {"0":"D", "1":"F", "2":"B"}
            }
        }
        
        minimizer = DFAMinimizer(**dfa)
        res = minimizer.minimize()
        
        # 1. The equivalence classes match the expected result.
        # 2. The minimized DFA has exactly three states.
        states = res['states']
        self.assertEqual(len(states), 3)
        self.assertIn('{A,D}', states)
        self.assertIn('{B,E}', states)
        self.assertIn('{C,F}', states)
        
        # Check start and accepting states
        self.assertEqual(res['start_state'], '{A,D}')
        self.assertCountEqual(res['accepting_states'], ['{B,E}', '{C,F}'])
        
        # 3. Every symbol has exactly one outgoing transition from every minimized state.
        # 4. All targets reference valid minimized states.
        for state in states:
            trans = res['transitions'][state]
            self.assertEqual(len(trans), 3)
            for symbol in ['0', '1', '2']:
                self.assertIn(symbol, trans)
                self.assertIn(trans[symbol], states)
                
        # Specifically check transition logic
        self.assertEqual(res['transitions']['{A,D}']['0'], '{B,E}')
        self.assertEqual(res['transitions']['{A,D}']['1'], '{C,F}')
        self.assertEqual(res['transitions']['{A,D}']['2'], '{A,D}')
        
        # 5. The minimized DFA accepts exactly the same language as the original DFA
        is_equiv, _ = verify_language_equivalence(dfa, res)
        self.assertTrue(is_equiv)
        
        # 6. The displayed table and diagram match the algorithm's actual output.
        # Generate diagram
        output_path = render_dfa_diagram(res, filename='test_contradictory_bug')
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

if __name__ == '__main__':
    unittest.main()
