import unittest
from core.universal_generator import solve_universal

class TestRegexToDFA(unittest.TestCase):
    def test_regex_conversion(self):
        data = {
            "regex": "(0|1)*01",
            "alphabet": ["0", "1"],
            "strings": ["01", "101", "1101", "0", "10", ""]
        }
        
        result = solve_universal("String Acceptance Traces", data)
        html = result['subquestions'][0]['answer']
        
        # Verify pipeline execution
        self.assertIn("&epsilon;-NFA &rarr; DFA &rarr; Minimized DFA", html)
        self.assertIn("mode_b_regex_dfa", html)
        
        # Verify strings
        self.assertIn("<strong>01</strong>: Accepted", html)
        self.assertIn("<strong>101</strong>: Accepted", html)
        self.assertIn("<strong>1101</strong>: Accepted", html)
        
        self.assertIn("<strong>0</strong>: Rejected", html)
        self.assertIn("<strong>10</strong>: Rejected", html)
        self.assertIn("<strong></strong>: Rejected", html)

    def test_malformed_regex(self):
        data = {
            "regex": "(0|1**01", # Malformed
            "alphabet": ["0", "1"]
        }
        result = solve_universal("String Acceptance Traces", data)
        html = result['subquestions'][0]['answer']
        
        self.assertIn("Regex Parsing Error", html)
        self.assertNotIn("mode_b_regex_dfa", html)

if __name__ == '__main__':
    unittest.main()
