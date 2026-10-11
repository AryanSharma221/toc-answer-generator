import unittest
from core.universal_generator import solve_universal

class TestCFGAmbiguityExplainer(unittest.TestCase):
    def test_ambiguity_explainer(self):
        grammar = "E -> E '+' E | E '*' E | 'id'"
        # Token array: ['id', '+', 'id', '*', 'id']
        tokens = ['id', '+', 'id', '*', 'id']
        
        data = {
            "grammar": grammar,
            "start_symbol": "E",
            "input_tokens": tokens
        }
        
        result = solve_universal("CFG Derivation", data)
        html = result['subquestions'][0]['answer']
        
        # Verify both trees exist
        self.assertIn("mode_b_cfg_tree_0", html)
        self.assertIn("mode_b_cfg_tree_1", html)
        
        # Verify the explanation exists
        self.assertIn("Ambiguity Structural Difference", html)
        
        # The explanation should mention the rules where it diverged
        self.assertIn("E -&gt; E '*' E", html.replace("->", "-&gt;"))
        self.assertIn("E -&gt; E '+' E", html.replace("->", "-&gt;"))
        
        # Verify terminal sequences
        # Derivation 1
        self.assertIn("&rArr; id + id * id", html)

if __name__ == '__main__':
    unittest.main()
