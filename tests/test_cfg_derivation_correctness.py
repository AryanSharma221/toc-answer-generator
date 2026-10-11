import sys
import unittest
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from solvers.cfg_solver import CFGSolver
from core.universal_generator import solve_universal

class TestCFGDerivationCorrectness(unittest.TestCase):
    def setUp(self):
        self.grammar = "S -> ( S ) S | epsilon"
        self.start_sym = "S"

    def test_exact_regression_example_step_by_step(self):
        """
        Verify the exact regression example specified in requirements:
        Grammar: S -> ( S ) S | epsilon
        Start symbol: S
        Target string: (())()
        Derivation: Leftmost

        Expected exact derivation sequence:
        Step 0: S
        Step 1: (S)S
        Step 2: ((S)S)S
        Step 3: (()S)S
        Step 4: (())S
        Step 5: (())(S)S
        Step 6: (())()S
        Step 7: (())()
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input("(())()")
        trees = solver.parse(tokens)
        self.assertIsInstance(trees, list)
        self.assertGreater(len(trees), 0, "Parser must find at least one parse tree")
        
        tree = trees[0]
        steps = solver.get_detailed_derivation(tree, mode="leftmost")
        
        expected_sequence = [
            (0, "S", None, None),
            (1, "(S)S", "S", "S -> ( S ) S"),
            (2, "((S)S)S", "S", "S -> ( S ) S"),
            (3, "(()S)S", "S", "S -> ε"),
            (4, "(())S", "S", "S -> ε"),
            (5, "(())(S)S", "S", "S -> ( S ) S"),
            (6, "(())()S", "S", "S -> ε"),
            (7, "(())()", "S", "S -> ε"),
        ]
        
        self.assertEqual(len(steps), len(expected_sequence), f"Derivation must have exactly {len(expected_sequence)} steps")
        
        print("\n--- REGRESSION EXAMPLE STEP-BY-STEP COMPARISON ---")
        for idx, (exp_idx, exp_form, exp_nt, exp_prod) in enumerate(expected_sequence):
            actual_step = steps[idx]
            actual_idx = actual_step["index"]
            actual_form = actual_step["form"]
            actual_nt = actual_step["expanded"]
            actual_prod = actual_step["production"]
            
            print(f"Step {actual_idx}: Actual='{actual_form}' vs Expected='{exp_form}' (Rule: {actual_prod})")
            
            self.assertEqual(actual_idx, exp_idx, f"Step index mismatch at step {idx}")
            self.assertEqual(actual_form, exp_form, f"Sentential form mismatch at step {idx}")
            if exp_nt is not None:
                self.assertEqual(actual_nt, exp_nt, f"Expanded non-terminal mismatch at step {idx}")
            if exp_prod is not None:
                self.assertEqual(actual_prod, exp_prod, f"Applied production mismatch at step {idx}")
                
        err = solver.validate_derivation(steps, tokens, mode="leftmost", tree=tree)
        self.assertIsNone(err, f"Derivation validation failed: {err}")
        self.assertEqual(steps[-1]["form"], "(())()")

    def test_rightmost_derivation_exact_steps(self):
        """
        Verify rightmost derivation for (())()
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input("(())()")
        trees = solver.parse(tokens)
        tree = trees[0]
        steps = solver.get_detailed_derivation(tree, mode="rightmost")
        
        expected_rightmost = [
            (0, "S"),
            (1, "(S)S"),
            (2, "(S)(S)S"),
            (3, "(S)(S)"),
            (4, "(S)()"),
            (5, "((S)S)()"),
            (6, "((S))()"),
            (7, "(())()"),
        ]
        
        self.assertEqual(len(steps), len(expected_rightmost))
        for idx, (exp_idx, exp_form) in enumerate(expected_rightmost):
            self.assertEqual(steps[idx]["index"], exp_idx)
            self.assertEqual(steps[idx]["form"], exp_form)
            
        err = solver.validate_derivation(steps, tokens, mode="rightmost", tree=tree)
        self.assertIsNone(err)

    def test_epsilon_derivation(self):
        """
        Verify empty target string (epsilon)
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input("epsilon")
        trees = solver.parse(tokens)
        self.assertEqual(len(trees), 1)
        steps = solver.get_detailed_derivation(trees[0], mode="leftmost")
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["form"], "S")
        self.assertEqual(steps[1]["form"], "ε")
        self.assertEqual(steps[1]["production"], "S -> ε")
        err = solver.validate_derivation(steps, tokens, mode="leftmost", tree=trees[0])
        self.assertIsNone(err)

    def test_generalization_non_hardcoded(self):
        """
        Requirement 9: Do not hardcode the example.
        Test with an expression grammar: E -> E + T | T, T -> id
        """
        expr_grammar = "E -> E + T | T\nT -> id"
        solver = CFGSolver(expr_grammar, "E")
        tokens = solver.tokenize_input("id + id")
        trees = solver.parse(tokens)
        self.assertEqual(len(trees), 1)
        steps = solver.get_detailed_derivation(trees[0], mode="leftmost")
        
        # E -> E + T -> T + T -> id + T -> id + id
        expected_forms = ["E", "E + T", "T + T", "id + T", "id + id"]
        actual_forms = [s["form"] for s in steps]
        self.assertEqual(actual_forms, expected_forms)
        err = solver.validate_derivation(steps, tokens, mode="leftmost", tree=trees[0])
        self.assertIsNone(err)

    def test_invalid_string_rejection_no_partial_success(self):
        """
        Requirements 7 & 8: Continue until exact target or reject.
        Never report success for partial derivation.
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input("(()")
        trees = solver.parse(tokens)
        self.assertEqual(len(trees), 0)
        
        # Test through solve_universal
        data = {
            "grammar": self.grammar,
            "start_symbol": self.start_sym,
            "input_tokens": "(()",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        ans = res["subquestions"][0]["answer"]
        self.assertIn("Rejected", ans)
        self.assertIn("not generated by the grammar", ans)
        self.assertNotIn("mode_b_cfg_tree", ans)

    def test_resource_limits_report_incomplete_not_false_negative(self):
        """
        Requirement 10: If solver cannot complete search within resource limits,
        report an incomplete search rather than false negative (not 'Rejected').
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        # Parse with max_tokens limit of 5 tokens
        res_limited = solver.parse("(())(())", max_tokens=5)
        self.assertIsInstance(res_limited, str)
        self.assertIn("Search incomplete", res_limited)
        self.assertIn("exceeds resource limit", res_limited)
        
        # Test solve_universal reports Search Incomplete, NOT Rejected
        data = {
            "grammar": self.grammar,
            "start_symbol": self.start_sym,
            "input_tokens": " ".join(["("]*160 + [")"]*160), # 320 tokens > 300 limit
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        ans = res["subquestions"][0]["answer"]
        self.assertIn("Search Incomplete", ans)
        self.assertNotIn("Rejected", ans)
        self.assertIn("exceeds resource limit", ans)

    def test_solve_universal_both_modes_regression_case(self):
        for mode in ["Leftmost", "Rightmost"]:
            data = {
                "grammar": self.grammar,
                "start_symbol": self.start_sym,
                "input_tokens": "( ( ) ) ( )",
                "derivation": mode
            }
            res = solve_universal("CFG Derivation", data)
            ans = res["subquestions"][0]["answer"]
            self.assertIn("Accepted", ans)
            self.assertIn("Final Answer", ans)
            self.assertIn("(())()", ans)
            self.assertIn("mode_b_cfg_tree", ans)

if __name__ == '__main__':
    unittest.main()
