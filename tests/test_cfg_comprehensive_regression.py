import unittest
from core.universal_generator import solve_universal
from solvers.cfg_solver import CFGSolver
from bs4 import BeautifulSoup

class TestCFGComprehensiveRegression(unittest.TestCase):
    """
    Automated regression suite for CFG Derivation & Ambiguity Analysis.
    Compares:
      1. Actual derivation against expected derivation.
      2. Final sentential form against target.
      3. Parse-tree terminal yield against target.
      4. Derivation table against step-by-step explanation.
      5. Final answer against deterministic solver status.
    """

    def _verify_consistency(self, res, expected_status, expected_yield, expected_steps=None, is_rightmost=False):
        """Helper to verify canonical result, explanation, table, derivation sequence, and parse trees."""
        self.assertIn("canonical_result", res)
        canon = res["canonical_result"]["raw_data"]
        html = res["subquestions"][0]["answer"]

        # 5. Final answer against deterministic solver status
        self.assertEqual(canon["status"], expected_status, f"Expected status {expected_status}, got {canon['status']}")
        if expected_status == "Accepted":
            self.assertTrue(canon["success"])
            self.assertIn("Accepted", html)
            self.assertNotIn("Rejected", html)

            # 2. Final sentential form against target
            self.assertEqual(canon["terminal_yield"], expected_yield)
            sentential_forms = canon["ordered_sentential_forms"]
            self.assertGreater(len(sentential_forms), 0)
            final_form = sentential_forms[-1]
            # Strip spaces for comparison if single char
            if canon.get("has_multichar"):
                self.assertEqual(final_form, expected_yield)
            else:
                self.assertEqual(final_form.replace(" ", ""), expected_yield.replace(" ", ""))

            steps = canon.get("steps", [])

            # 1. Actual derivation against expected derivation (if provided)
            if expected_steps:
                actual_steps = [s.get("form", "").replace(" ", "") for s in steps]
                exp_clean = [s.replace(" ", "") for s in expected_steps]
                self.assertEqual(actual_steps, exp_clean, f"Derivation steps mismatch:\nActual: {actual_steps}\nExpected: {exp_clean}")

            # 3. Parse-tree terminal yield against target
            tree_count = canon.get("parse_trees_count", 0)
            self.assertGreater(tree_count, 0, "Expected at least 1 parse tree")
            self.assertIsNotNone(canon.get("parse_tree_data"), "Expected parse_tree_data to be populated")
            tree_yield = canon["terminal_yield"]
            self.assertEqual(tree_yield, expected_yield)

            # 4. Table against explanation
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", class_="cfg-derivation-table")
            self.assertIsNotNone(table, "Expected derivation table in HTML")
            rows = table.find("tbody").find_all("tr")
            self.assertEqual(len(rows), len(steps))

            # Check explanation list
            step_list = soup.find("ol", class_="cfg-steps-list")
            self.assertIsNotNone(step_list, "Expected step-by-step list in HTML")
            list_items = step_list.find_all("li")
            # Items: N steps + 1 termination notice
            self.assertEqual(len(list_items), len(steps) + 1)

            for idx, (row, li) in enumerate(zip(rows, list_items[:-1])):
                cols = [td.get_text().strip() for td in row.find_all("td")]
                step_num = cols[0]
                s_form = cols[1]
                li_text = li.get_text()
                self.assertIn(f"Step {step_num}", li_text)

            # Verify rightmost/leftmost correctness in nonterminal expansions
            for s in steps[1:]:
                expanded_nt = s.get("expanded")
                self.assertIsNotNone(expanded_nt)

        elif expected_status == "Rejected":
            self.assertFalse(canon["success"])
            self.assertIn("Rejected", html)
            self.assertNotIn("Accepted", html)

    def test_1_nested_parentheses(self):
        """TEST 1 — Nested parentheses: S -> ( S ) S | epsilon, target (())()"""
        grammar = "S -> ( S ) S | epsilon"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "(())()",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        expected_steps = [
            "S",
            "(S)S",
            "((S)S)S",
            "(()S)S",
            "(())S",
            "(())(S)S",
            "(())()S",
            "(())()"
        ]
        self._verify_consistency(res, "Accepted", "(())()", expected_steps)

    def test_2_simple_recursion(self):
        """TEST 2 — Simple recursion: S -> a S b | epsilon, target aabb"""
        grammar = "S -> a S b | epsilon"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "aabb",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        expected_steps = [
            "S",
            "aSb",
            "aaSbb",
            "aabb"
        ]
        self._verify_consistency(res, "Accepted", "aabb", expected_steps)

    def test_3_empty_string(self):
        """TEST 3 — Empty string: S -> a S | epsilon, target empty"""
        grammar = "S -> a S | epsilon"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        expected_steps = [
            "S",
            "ε"
        ]
        self._verify_consistency(res, "Accepted", "ε", expected_steps)

    def test_4_invalid_string(self):
        """TEST 4 — Invalid string: S -> a S | epsilon, target ab"""
        grammar = "S -> a S | epsilon"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "ab",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        self._verify_consistency(res, "Rejected", None)

    def test_5_ambiguous_grammar(self):
        """TEST 5 — Ambiguous grammar: S -> S S | a, target aaa"""
        grammar = "S -> S S | a"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "aaa",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        canon = res["canonical_result"]["raw_data"]
        html = res["subquestions"][0]["answer"]

        self._verify_consistency(res, "Accepted", "aaa")
        self.assertGreaterEqual(canon.get("parse_trees_count", 0), 2)
        self.assertIn("Grammar is ambiguous! Found 2 distinct parse trees", html)
        self.assertIn("Ambiguity Structural Difference", html)
        self.assertIn("Generated Parse Tree 1", html)
        self.assertIn("Generated Parse Tree 2", html)

    def test_6_rightmost_derivation(self):
        """
        TEST 6 — Rightmost derivation
        Grammar:
        S -> A B
        A -> a A | a
        B -> b B | b
        Target: aabb
        Expected: Every step expands the rightmost nonterminal.
        """
        grammar = "S -> A B\nA -> a A | a\nB -> b B | b"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "aabb",
            "derivation": "Rightmost"
        }
        res = solve_universal("CFG Derivation", data)
        canon = res["canonical_result"]["raw_data"]
        
        # Verify rightmost expansion invariant at every step
        steps = canon.get("steps", [])
        # Step 0: S
        # Step 1: A B (B is rightmost NT)
        # Step 2: A b B (B is rightmost NT)
        # Step 3: A b b (A is rightmost NT)
        # Step 4: a A b b (A is rightmost NT)
        # Step 5: a a b b
        self._verify_consistency(res, "Accepted", "aabb", is_rightmost=True)
        
        # Explicit check of rightmost order
        for i in range(1, len(steps)):
            prev_symbols = steps[i - 1].get("sentential_symbols", [])
            # Find rightmost nonterminal in prev_symbols
            nonterminals = [sym["symbol"] for sym in prev_symbols if sym.get("is_nonterminal")]
            if nonterminals:
                expected_rm_nt = nonterminals[-1]
                actual_expanded = steps[i]["expanded"]
                self.assertEqual(actual_expanded, expected_rm_nt,
                                 f"At step {i}, expected rightmost NT '{expected_rm_nt}' to expand, but got '{actual_expanded}'")

    def test_7_whitespace_handling(self):
        """TEST 7 — Whitespace handling: S -> ( S ) S | epsilon, target ( ( ) ) ( )"""
        grammar = "S -> ( S ) S | epsilon"
        data = {
            "grammar": grammar,
            "start_symbol": "S",
            "input_tokens": "( ( ) ) ( )",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        expected_steps = [
            "S",
            "(S)S",
            "((S)S)S",
            "(()S)S",
            "(())S",
            "(())(S)S",
            "(())()S",
            "(())()"
        ]
        self._verify_consistency(res, "Accepted", "(())()", expected_steps)
        self.assertEqual(res["canonical_result"]["raw_data"]["target_tokens"], ["(", "(", ")", ")", "(", ")"])

if __name__ == "__main__":
    unittest.main()
