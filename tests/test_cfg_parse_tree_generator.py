import os
import sys
import unittest
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from solvers.cfg_solver import CFGSolver
from core.universal_generator import solve_universal
from diagrams.parse_tree_renderer import render_parse_tree

class TestCFGParseTreeGenerator(unittest.TestCase):
    def test_grammar_1_parentheses_regression(self):
        """
        TEST GRAMMAR:
        S -> ( S ) S | epsilon
        TARGET:
        (())()

        EXPECTED:
        The parse tree must generate exactly six terminal symbols in this order:
        ( ( ) ) ( )
        The root must be S, and every internal node must correspond to a valid production.
        """
        grammar = "S -> ( S ) S | epsilon"
        start_sym = "S"
        solver = CFGSolver(grammar, start_sym)
        tokens = solver.tokenize_input("(())()")
        trees = solver.parse(tokens)
        self.assertEqual(len(trees), 1)
        
        for mode in ["Leftmost", "Rightmost"]:
            canonical = solver.build_canonical_derivation(trees[0], tokens, mode=mode)
            self.assertTrue(canonical["parse_tree_verified"])
            self.assertIsNone(canonical["parse_tree_error"])
            
            tree_data = canonical["parse_tree_data"]
            self.assertIsNotNone(tree_data)
            
            # 1. Root must be S
            self.assertEqual(tree_data["label"], "S")
            
            # 2. Unique node identifiers across entire tree
            all_node_ids = set()
            def collect_ids(node):
                nid = node["id"]
                self.assertNotIn(nid, all_node_ids, f"Duplicate node ID found: {nid}")
                all_node_ids.add(nid)
                for child in node.get("children", []):
                    collect_ids(child)
            collect_ids(tree_data)
            self.assertGreater(len(all_node_ids), 10)
            
            # 3. Terminal yield must generate exactly six terminal symbols in order: ( ( ) ) ( )
            term_yield = solver.get_tree_terminal_yield(tree_data)
            expected_yield = ["(", "(", ")", ")", "(", ")"]
            self.assertEqual(term_yield, expected_yield, f"Failed in mode {mode}")
            
            # 4. Check epsilon productions correctly present as explicit leaves
            eps_nodes = []
            def collect_eps(node):
                if node.get("label") == "ε":
                    eps_nodes.append(node)
                for child in node.get("children", []):
                    collect_eps(child)
            collect_eps(tree_data)
            self.assertEqual(len(eps_nodes), 4, f"Expected 4 epsilon leaves for (())() derivation in {mode} mode")
            
            # 5. Render diagram and verify file exists
            img_path = render_parse_tree(tree_data, filename=f"test_grammar_1_{mode}")
            self.assertTrue(os.path.exists(img_path))
            self.assertGreater(os.path.getsize(img_path), 0)
            if os.path.exists(img_path):
                os.remove(img_path)

    def test_grammar_2_aabb_regression(self):
        """
        TEST ANOTHER GRAMMAR:
        S -> a S b | epsilon
        TARGET:
        aabb

        EXPECTED:
        Terminal leaves: a a b b
        """
        grammar = "S -> a S b | epsilon"
        start_sym = "S"
        solver = CFGSolver(grammar, start_sym)
        tokens = solver.tokenize_input("aabb")
        trees = solver.parse(tokens)
        self.assertEqual(len(trees), 1)
        
        for mode in ["Leftmost", "Rightmost"]:
            canonical = solver.build_canonical_derivation(trees[0], tokens, mode=mode)
            self.assertTrue(canonical["parse_tree_verified"])
            tree_data = canonical["parse_tree_data"]
            
            # Root must be S
            self.assertEqual(tree_data["label"], "S")
            
            # Terminal yield must be ['a', 'a', 'b', 'b']
            term_yield = solver.get_tree_terminal_yield(tree_data)
            self.assertEqual(term_yield, ["a", "a", "b", "b"])
            
            # Check 1 epsilon leaf at the bottom
            eps_nodes = []
            def collect_eps(node):
                if node.get("label") == "ε":
                    eps_nodes.append(node)
                for child in node.get("children", []):
                    collect_eps(child)
            collect_eps(tree_data)
            self.assertEqual(len(eps_nodes), 1)
            
            # Render diagram
            img_path = render_parse_tree(tree_data, filename=f"test_grammar_2_{mode}")
            self.assertTrue(os.path.exists(img_path))
            if os.path.exists(img_path):
                os.remove(img_path)

    def test_verification_failure_handling(self):
        """
        Requirement 6 & 7: Verify that if verification fails, an error is reported
        rather than an incorrect tree.
        """
        grammar = "S -> a S b | epsilon"
        solver = CFGSolver(grammar, "S")
        tokens = solver.tokenize_input("aabb")
        tree = solver.parse(tokens)[0]
        steps = solver.get_detailed_derivation(tree, mode="leftmost")
        
        # Build valid tree
        valid_tree = solver.build_tree_from_derivation(steps, mode="leftmost")
        
        # Test verification against wrong tokens
        is_valid, err_msg = solver.verify_tree_terminal_yield(valid_tree, ["a", "b"])
        self.assertFalse(is_valid)
        self.assertIn("mismatch", err_msg)
        
        # Test None tree
        is_valid_none, err_none = solver.verify_tree_terminal_yield(None, ["a", "b"])
        self.assertFalse(is_valid_none)

    def test_solve_universal_parse_tree_rendering_and_controls(self):
        """
        Requirement 10: Preserve Fit, Zoom In, Zoom Out, and Reset controls.
        Verify end-to-end HTML answer.
        """
        data = {
            "grammar": "S -> ( S ) S | epsilon",
            "start_symbol": "S",
            "input_tokens": "( ( ) ) ( )",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        html_answer = res["subquestions"][0]["answer"]
        
        # Diagram figure and image presence
        self.assertIn("Generated Parse Tree 1", html_answer)
        self.assertIn("data:image/png;base64,", html_answer)
        
        # Verify zoom controls
        self.assertIn("Fit", html_answer)
        self.assertIn("Zoom In (+)", html_answer)
        self.assertIn("Zoom Out (-)", html_answer)
        self.assertIn("Reset", html_answer)
        self.assertIn("zoom_img", html_answer)

    def test_nested_recursion_and_repeated_nonterminals(self):
        """
        Requirement 8: Support nested recursion and repeated nonterminals.
        Grammar with multiple repeated nonterminals per rule:
        E -> E + E | E * E | a
        Target: a + a * a
        """
        grammar = "E -> E + E | E * E | a"
        solver = CFGSolver(grammar, "E")
        tokens = solver.tokenize_input("a + a * a")
        trees = solver.parse(tokens)
        self.assertGreater(len(trees), 0)
        
        for t in trees:
            canonical = solver.build_canonical_derivation(t, tokens, mode="Leftmost")
            self.assertTrue(canonical["parse_tree_verified"])
            tree_data = canonical["parse_tree_data"]
            self.assertEqual(tree_data["label"], "E")
            
            term_yield = solver.get_tree_terminal_yield(tree_data)
            self.assertEqual(term_yield, ["a", "+", "a", "*", "a"])

if __name__ == '__main__':
    unittest.main()
