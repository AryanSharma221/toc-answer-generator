import unittest
import os
import shutil
from diagrams.dfa_renderer import render_dfa_diagram, validate_dfa_diagram_data, validate_rendered_diagram

class TestDFARenderer(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'output/test_figures'
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_valid_input_and_rendering(self):
        dfa = {
            'states': ['A', 'B'],
            'alphabet': ['0', '1'],
            'start_state': 'A',
            'accepting_states': ['B'],
            'transitions': {
                'A': {'0': 'B', '1': 'A'},
                'B': {'0': 'B', '1': 'A'}
            }
        }
        
        # Test validation
        validate_dfa_diagram_data(dfa)
        
        # Test rendering
        output_path = render_dfa_diagram(dfa, filename='test_valid', directory=self.test_dir)
        
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
        self.assertTrue(validate_rendered_diagram(output_path))

    def test_invalid_input_missing_key(self):
        dfa = {
            'states': ['A', 'B'],
            # missing alphabet
            'start_state': 'A',
            'accepting_states': ['B'],
            'transitions': {}
        }
        with self.assertRaises(ValueError) as cm:
            validate_dfa_diagram_data(dfa)
        self.assertIn("missing key 'alphabet'", str(cm.exception))

    def test_invalid_start_state(self):
        dfa = {
            'states': ['A', 'B'],
            'alphabet': ['0', '1'],
            'start_state': 'C', # Invalid
            'accepting_states': ['B'],
            'transitions': {}
        }
        with self.assertRaises(ValueError) as cm:
            validate_dfa_diagram_data(dfa)
        self.assertIn("must be in 'states'", str(cm.exception))

    def test_self_loops_and_multiple_transitions(self):
        # A has self-loop on 0 and 1.
        # This tests both self-loops and grouping multiple transitions.
        dfa = {
            'states': ['A', 'B'],
            'alphabet': ['0', '1', '2'],
            'start_state': 'A',
            'accepting_states': [],
            'transitions': {
                'A': {'0': 'A', '1': 'A', '2': 'B'}
            }
        }
        
        output_path = render_dfa_diagram(dfa, filename='test_loops', directory=self.test_dir)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
        
    def test_accepting_states_and_merged_labels(self):
        # Test formatted string states like {A,B}
        dfa = {
            'states': ['{A,B}', 'C'],
            'alphabet': ['0', '1'],
            'start_state': '{A,B}',
            'accepting_states': ['{A,B}'],
            'transitions': {
                '{A,B}': {'0': '{A,B}', '1': 'C'},
                'C': {'0': '{A,B}', '1': 'C'}
            }
        }
        output_path = render_dfa_diagram(dfa, filename='test_accepting', directory=self.test_dir)
        self.assertTrue(os.path.exists(output_path))

if __name__ == '__main__':
    unittest.main()
