import unittest
from bs4 import BeautifulSoup
from core.universal_generator import solve_universal
from solvers.cfg_solver import CFGSolver

class TestCFGAmbiguityTokenization(unittest.TestCase):
    """
    Comprehensive verification suite for CFG input validation, tokenization,
    and ambiguity analysis requirements.
    """

    def test_requirement_1_and_2_ignore_formatting_whitespace_between_terminals(self):
        """
        Requirements 1 & 2:
        - Target string with spaces between single-character terminals: '( ( ) ) ( )'
        - Spaces are token separators, not terminals.
        - Resulting terminal yield must be '(())()' without space tokens.
        """
        grammar = "S -> ( S ) S | epsilon"
        start_symbol = "S"
        target_str = "( ( ) ) ( )"
        data = {
            "grammar": grammar,
            "start_symbol": start_symbol,
            "input_tokens": target_str,
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        self.assertIn("subquestions", res)
        html = res["subquestions"][0]["answer"]

        # Status must be Accepted
        self.assertIn("Accepted", html)
        self.assertNotIn("Rejected", html)
        self.assertNotIn("Grammar does not cover some of the input words: ' '", html)

        # Check derivation steps and canonical result
        canon = res.get("canonical_result", {}).get("raw_data")
        self.assertIsNotNone(canon)
        self.assertEqual(canon["target_tokens"], ["(", "(", ")", ")", "(", ")"])
        self.assertEqual(canon["terminal_yield"], "(())()")
        self.assertTrue(canon["success"])

        # Also test compact target string
        data_compact = {
            "grammar": grammar,
            "start_symbol": start_symbol,
            "input_tokens": "(())()",
            "derivation": "Leftmost"
        }
        res_compact = solve_universal("CFG Derivation", data_compact)
        canon_compact = res_compact.get("canonical_result", {}).get("raw_data")
        self.assertEqual(canon_compact["target_tokens"], ["(", "(", ")", ")", "(", ")"])
        self.assertEqual(canon_compact["terminal_yield"], "(())()")

    def test_requirement_3_preserve_spaces_inside_quoted_terminals(self):
        """
        Requirement 3:
        Preserve spaces inside quoted multi-character terminals (e.g. 'a b').
        """
        grammar = "S -> 'a b' S | 'c'"
        start_symbol = "S"
        target = "'a b' c"
        data = {
            "grammar": grammar,
            "start_symbol": start_symbol,
            "input_tokens": target,
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        html = res["subquestions"][0]["answer"]
        self.assertIn("Accepted", html)
        canon = res.get("canonical_result", {}).get("raw_data")
        self.assertEqual(canon["target_tokens"], ["a b", "c"])
        self.assertEqual(canon["terminal_yield"], "a b c")

    def test_requirement_4_support_various_terminals(self):
        """
        Requirement 4:
        Support terminals such as a, b, 0, 1, (, and ).
        """
        grammar = "S -> '0' S '1' | 'a' S 'b' | '(' S ')' | epsilon"
        start_symbol = "S"
        solver = CFGSolver(grammar, start_symbol)
        expected_terminals = {"0", "1", "a", "b", "(", ")"}
        self.assertTrue(expected_terminals.issubset(solver.terminals))

        # Test valid parsing with numbers and parens
        data = {
            "grammar": grammar,
            "start_symbol": start_symbol,
            "input_tokens": "0 ( a b ) 1",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        canon = res.get("canonical_result", {}).get("raw_data")
        self.assertTrue(canon["success"])
        self.assertEqual(canon["terminal_yield"], "0(ab)1")

    def test_requirement_5_epsilon_treatment(self):
        """
        Requirement 5:
        Treat epsilon as empty production, not as an input token.
        """
        grammar = "S -> a S b | epsilon"
        solver = CFGSolver(grammar, "S")
        # Tokenizing epsilon should return empty list
        self.assertEqual(solver.tokenize_input("epsilon"), [])
        self.assertEqual(solver.tokenize_input("eps"), [])
        self.assertEqual(solver.tokenize_input("ε"), [])
        self.assertEqual(solver.tokenize_input(""), [])
        # Epsilon within target should be omitted
        self.assertEqual(solver.tokenize_input("a eps b"), ["a", "b"])

    def test_requirement_6_reject_unsupported_grammar_syntax_and_undefined_nt(self):
        """
        Requirement 6:
        Reject undefined nonterminals and unsupported grammar syntax with useful error messages.
        """
        # Missing ->
        with self.assertRaises(ValueError):
            CFGSolver("S a S b", "S")

        # Empty LHS
        with self.assertRaises(ValueError):
            CFGSolver("-> a", "S")

        # Undefined start symbol
        with self.assertRaises(ValueError):
            CFGSolver("S -> a", "Z")

        # Empty grammar
        with self.assertRaises(ValueError):
            CFGSolver("", "S")

        # Undefined non-terminal on RHS
        solver_undef = CFGSolver("S -> A B\nA -> a", "S")
        self.assertIn("B", solver_undef.undefined_nonterminals)
        parse_res = solver_undef.parse(["a"])
        self.assertIsInstance(parse_res, str)
        self.assertIn("undefined non-terminal", parse_res)

    def test_requirement_7_empty_target_string_handling(self):
        """
        Requirement 7:
        Handle an empty target string correctly.
        """
        # 1. Grammar that derives epsilon
        grammar = "S -> ( S ) | epsilon"
        data_empty = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "",
            "derivation": "Leftmost"
        }
        res_empty = solve_universal("CFG Derivation", data_empty)
        canon_empty = res_empty.get("canonical_result", {}).get("raw_data")
        self.assertTrue(canon_empty["success"])
        self.assertEqual(canon_empty["terminal_yield"], "ε")

        # 2. Grammar that does NOT derive epsilon
        grammar_no_eps = "S -> ( S )"
        data_no_eps = {
            "grammar": grammar_no_eps,
            "start_symbol": "S",
            "input_tokens": "",
            "derivation": "Leftmost"
        }
        res_no_eps = solve_universal("CFG Derivation", data_no_eps)
        canon_no_eps = res_no_eps.get("canonical_result", {}).get("raw_data")
        self.assertFalse(canon_no_eps["success"])
        self.assertEqual(canon_no_eps["status"], "Rejected")

    def test_requirement_8_and_9_avoid_infinite_loops_and_resource_limits(self):
        """
        Requirements 8 & 9:
        Avoid infinite loops for recursive grammars and implement resource limits
        without reporting false success or false impossibility.
        """
        # Exceed max tokens limit
        grammar = "S -> S S | a"
        solver = CFGSolver(grammar, "S")
        huge_input = ["a"] * 350
        res = solver.parse(huge_input, max_tokens=300)
        self.assertIsInstance(res, str)
        self.assertIn("Search incomplete", res)
        self.assertIn("resource limit", res)

        # In universal generator, search incomplete status is handled without false rejection
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": huge_input,
            "derivation": "Leftmost"
        }
        gen_res = solve_universal("CFG Derivation", data)
        canon = gen_res.get("canonical_result", {}).get("raw_data")
        self.assertEqual(canon["status"], "Search Incomplete")
        html = gen_res["subquestions"][0]["answer"]
        self.assertIn("Search Incomplete", html)
        self.assertIn("Ambiguity is undetermined", html)

    def test_requirement_10_ambiguity_analysis_and_multiple_parse_trees(self):
        """
        Requirement 10 & Ambiguity Requirements:
        - Detect and display multiple distinct parse trees when parser finds them.
        - S -> S S | a with target 'a a a' has exactly 2 parse trees.
        - Report grammar is ambiguous.
        - Display both Generated Parse Tree 1 and Generated Parse Tree 2.
        """
        grammar = "S -> S S | a"
        start_symbol = "S"
        target = "a a a"
        data = {
            "grammar": grammar,
            "start_symbol": start_symbol,
            "input_tokens": target,
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        html = res["subquestions"][0]["answer"]

        # Must report ambiguity
        self.assertIn("Grammar is ambiguous! Found 2 distinct parse trees", html)
        self.assertIn("Ambiguity Structural Difference", html)

        # Must render both parse trees
        self.assertIn("Generated Parse Tree 1", html)
        self.assertIn("Generated Parse Tree 2", html)
        self.assertIn("mode_b_cfg_tree_0", html)
        self.assertIn("mode_b_cfg_tree_1", html)

        # Parse tree diagrams must both be present
        soup = BeautifulSoup(html, "html.parser")
        figures = soup.find_all("figure")
        tree_figs = [f for f in figures if "Generated Parse Tree" in f.get_text()]
        self.assertEqual(len(tree_figs), 2, f"Expected 2 parse tree figures, got {len(tree_figs)}")

    def test_unambiguous_string_wording_requirement(self):
        """
        If only one parse tree is found, clarify that only 1 tree was found
        for this specific string, and general grammar ambiguity remains unproven.
        """
        grammar = "S -> ( S ) S | epsilon"
        start_symbol = "S"
        target = "( ( ) ) ( )"
        data = {
            "grammar": grammar,
            "start_symbol": start_symbol,
            "input_tokens": target,
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        html = res["subquestions"][0]["answer"]
        self.assertIn("general grammar ambiguity is unproven", html)
        self.assertIn("Only 1 parse tree was found", html)

if __name__ == "__main__":
    unittest.main()
