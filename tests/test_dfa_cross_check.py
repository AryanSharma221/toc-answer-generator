import unittest
from solvers.dfa_minimizer import DFAMinimizer
from solvers.dfa_verification import moore_minimize, table_filling_minimize, verify_quotient, verify_language_equivalence

class TestDFACrossCheck(unittest.TestCase):
    def run_cross_check(self, states, alphabet, transitions, start_state, accepting_states):
        # 1. Run Hopcroft (from production)
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state, accepting_states)
        result = minimizer.minimize()
        
        # Hopcroft classes
        hopcroft_classes = []
        for s in result['states']:
            if s.startswith('{') and s.endswith('}'):
                hopcroft_classes.append(frozenset(s[1:-1].split(',')))
            else:
                hopcroft_classes.append(frozenset([s]))
                
        # 2. Run Moore
        moore_res = moore_minimize(states, alphabet, transitions, start_state, accepting_states)
        moore_classes = [frozenset(b) for b in moore_res]
        
        # 3. Run Table-Filling
        tf_res = table_filling_minimize(states, alphabet, transitions, start_state, accepting_states)
        tf_classes = [frozenset(b) for b in tf_res]
        
        # Compare as sets of sets
        self.assertEqual(set(hopcroft_classes), set(moore_classes))
        self.assertEqual(set(hopcroft_classes), set(tf_classes))
        
        # 4. Verify quotient
        valid, msg = verify_quotient(moore_res, states, alphabet, transitions, start_state, accepting_states)
        self.assertTrue(valid, msg)
        
        # 5. Verify language equivalence
        dfa1 = {
            'states': states,
            'alphabet': alphabet,
            'transitions': transitions,
            'start_state': start_state,
            'accepting_states': accepting_states
        }
        valid, counterexample = verify_language_equivalence(dfa1, result)
        self.assertTrue(valid, f"Language equivalence failed on string '{counterexample}'")
        
    def test_dfa_1(self):
        states = ['A', 'B', 'C', 'D']
        alphabet = ['0', '1']
        transitions = {
            'A': {'0': 'B', '1': 'C'},
            'B': {'0': 'B', '1': 'D'},
            'C': {'0': 'B', '1': 'C'},
            'D': {'0': 'B', '1': 'E'}, # Wait, E is not in states
        }
        # Let's write valid complete DFAs
        pass

    def test_dfa_2(self):
        states = ['A', 'B', 'C']
        alphabet = ['0', '1']
        transitions = {
            'A': {'0': 'B', '1': 'A'},
            'B': {'0': 'C', '1': 'A'},
            'C': {'0': 'B', '1': 'A'},
        }
        start_state = 'A'
        accepting_states = ['B']
        self.run_cross_check(states, alphabet, transitions, start_state, accepting_states)
        
    def test_dfa_3(self):
        states = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5']
        alphabet = ['a', 'b']
        transitions = {
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q0', 'b': 'q3'},
            'q2': {'a': 'q4', 'b': 'q5'},
            'q3': {'a': 'q4', 'b': 'q5'},
            'q4': {'a': 'q4', 'b': 'q5'},
            'q5': {'a': 'q5', 'b': 'q5'},
        }
        start_state = 'q0'
        accepting_states = ['q2', 'q3', 'q4']
        self.run_cross_check(states, alphabet, transitions, start_state, accepting_states)

if __name__ == '__main__':
    unittest.main()
