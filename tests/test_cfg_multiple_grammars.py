import unittest
from core.universal_generator import solve_universal

class TestCFGMultipleGrammars(unittest.TestCase):
    def run_cfg(self, grammar, string):
        tokens = list(string)
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": tokens
        }
        return solve_universal("CFG Derivation", data)

    def test_ambiguous_grammar_limits(self):
        grammar = "S -> SS | a | epsilon"
        res = self.run_cfg(grammar, "aaaa")
        html = res['subquestions'][0]['answer']
        
        # Verify it detected ambiguity and capped the result
        self.assertIn("Grammar is highly ambiguous!", html)
        self.assertIn("Found 100 distinct parse trees", html) # Since we bounded list() to 100
        self.assertIn("Rendering is capped to the first 10 trees", html)
        
        # Verify derivations exist
        self.assertIn("Leftmost Derivation", html)
        self.assertIn("Rightmost Derivation", html)
        self.assertIn("&rArr; a a a a", html)
        
    def test_unambiguous_concat(self):
        grammar = "S -> A B\nA -> a\nB -> b"
        res = self.run_cfg(grammar, "ab")
        html = res['subquestions'][0]['answer']
        self.assertIn("Only 1 parse tree was found", html)
        self.assertIn("&rArr; a b", html)

    def test_unsupported_string_reporting(self):
        grammar = "S -> a"
        res = self.run_cfg(grammar, "b")
        html = res['subquestions'][0]['answer']
        # The prompt says: "Report timeout or unsupported cases honestly. Never invent a derivation..."
        self.assertTrue("Grammar does not cover" in html or "not generated" in html)

if __name__ == '__main__':
    unittest.main()
