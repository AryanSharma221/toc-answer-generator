import unittest
import json
from core.universal_generator import solve_universal

class TestExistingDFAWorkflow(unittest.TestCase):
    def setUp(self):
        self.base_data = {
            "states": ["A", "B"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {
                "A": {"0": "B", "1": "A"},
                "B": {"0": "A", "1": "B"}
            },
            "strings": ["0", "1", "01", "10", "11", ""]
        }

    def test_valid_dfa_simulation(self):
        result = solve_universal("String Acceptance Traces", self.base_data)
        html = result['subquestions'][0]['answer']
        
        # 4. Displays reconstructed DFA
        self.assertIn("<img src=", html)
        self.assertIn("mode_b_orig_dfa", html)
        
        # 5, 6, 7, 8. Simulates strings, shows states, identifies final state, acceptance
        # "0": accepted (A -> B)
        self.assertIn("<strong>0</strong>: A --0--> B =&gt; <strong>Accepted</strong>", html.replace("=>", "=&gt;"))
        # "1": rejected (A -> A)
        self.assertIn("<strong>1</strong>: A --1--> A =&gt; <strong>Rejected</strong>", html.replace("=>", "=&gt;"))
        # "01": accepted (A -> B -> B)
        self.assertIn("<strong>01</strong>: A --0--> B --1--> B =&gt; <strong>Accepted</strong>", html.replace("=>", "=&gt;"))
        # "10": accepted (A -> A -> B)
        self.assertIn("<strong>10</strong>: A --1--> A --0--> B =&gt; <strong>Accepted</strong>", html.replace("=>", "=&gt;"))
        # "11": rejected (A -> A -> A)
        self.assertIn("<strong>11</strong>: A --1--> A --1--> A =&gt; <strong>Rejected</strong>", html.replace("=>", "=&gt;"))
        # "": rejected (A)
        self.assertIn("<strong></strong>: A =&gt; <strong>Rejected</strong>", html.replace("=>", "=&gt;"))

    def test_validation_unknown_state(self):
        data = dict(self.base_data)
        data['transitions'] = {
            "A": {"0": "C", "1": "A"}, # C is unknown
            "B": {"0": "A", "1": "B"}
        }
        result = solve_universal("String Acceptance Traces", data)
        html = result['subquestions'][0]['answer']
        self.assertIn("Validation Error", html)
        self.assertIn("leads to unknown state 'C'", html)

    def test_validation_missing_transition(self):
        data = dict(self.base_data)
        data['transitions'] = {
            "A": {"0": "B"}, # missing '1'
            "B": {"0": "A", "1": "B"}
        }
        result = solve_universal("String Acceptance Traces", data)
        html = result['subquestions'][0]['answer']
        self.assertIn("Validation Error", html)
        self.assertIn("Missing transition for state 'A' on symbol '1'", html)

    def test_validation_invalid_symbol(self):
        data = dict(self.base_data)
        data['transitions'] = {
            "A": {"0": "B", "1": "A", "2": "A"}, # 2 is invalid
            "B": {"0": "A", "1": "B"}
        }
        result = solve_universal("String Acceptance Traces", data)
        html = result['subquestions'][0]['answer']
        self.assertIn("Validation Error", html)
        self.assertIn("unknown symbol '2'", html)

if __name__ == '__main__':
    unittest.main()
