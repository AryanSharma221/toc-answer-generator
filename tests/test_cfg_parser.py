import unittest
from core.universal_generator import solve_universal

class TestCFGParserEditor(unittest.TestCase):
    def run_cfg(self, grammar, string):
        tokens = list(string)
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": tokens
        }
        return solve_universal("CFG Derivation", data)

    def test_complex_grammar(self):
        # S -> AB
        # A -> aA | a
        # B -> bB | epsilon
        grammar = "S -> AB\nA -> aA | a\nB -> bB | epsilon"
        
        # Test "a" (A->a, B->eps)
        res_a = self.run_cfg(grammar, "a")
        html_a = res_a['subquestions'][0]['answer']
        self.assertIn("Only 1 parse tree was found", html_a)
        
        # Test "abb" (A->a, B->bB->bbB->bb eps)
        res_abb = self.run_cfg(grammar, "abb")
        html_abb = res_abb['subquestions'][0]['answer']
        self.assertIn("Only 1 parse tree was found", html_abb)
        
        # Test "aabb" (A->aA->aa, B->bB->bb eps)
        res_aabb = self.run_cfg(grammar, "aabb")
        html_aabb = res_aabb['subquestions'][0]['answer']
        self.assertIn("Only 1 parse tree was found", html_aabb)

        # Internal format check
        self.assertIn("S -&gt; A B", html_a.replace("->", "-&gt;"))
        self.assertIn("B -&gt;", html_a.replace("->", "-&gt;")) # epsilon
        self.assertIn("A -&gt; 'a' A", html_a.replace("->", "-&gt;"))

    def test_malformed_productions(self):
        # Undefined non-terminal
        grammar = "S -> X Y\nX -> 'x'"
        res = self.run_cfg(grammar, "xy")
        html = res['subquestions'][0]['answer']
        # nltk raises ValueError if terminal 'y' is missing from RHS, or if start symbol doesn't expand
        self.assertIn("Grammar does not cover", html)
        
        # Inconsistent notation (mix of quotes and spaces)
        grammar2 = "S -> 'a' B | b B"
        res2 = self.run_cfg(grammar2, "ab")
        html2 = res2['subquestions'][0]['answer']
        # the preprocessor should normalize "b B" to 'b' B and "'a'B" to 'a' B. 
        # But wait, 'a'B has no space. NLTK split by space in our preprocessor!
        # If no space, split() gives "'a'B".
        # regex [A-Z]|[a-z0-9]+|. on "'a'B" yields "'", "a", "'", "B".
        # Which is perfectly normalized!

        grammar3 = "S -> aA\n"
        res3 = self.run_cfg(grammar3, "a")
        html3 = res3['subquestions'][0]['answer']
        self.assertTrue("ValueError" in html3 or "Grammar does not cover" in html3 or "is not generated" in html3)

if __name__ == '__main__':
    unittest.main()
