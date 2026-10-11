import sys
import os
import unittest
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from solvers.cfg_solver import CFGSolver
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html

class TestCFGPresentationConsistency(unittest.TestCase):
    def setUp(self):
        self.grammar = "S -> ( S ) S | epsilon"
        self.start_sym = "S"
        self.target_tokens = "( ( ) ) ( )"

    def test_canonical_structure_fields(self):
        """
        Requirement 1: Verify canonical structured derivation result contains all required fields.
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input(self.target_tokens)
        trees = solver.parse(tokens)
        self.assertEqual(len(trees), 1)
        tree = trees[0]
        
        canonical = solver.build_canonical_derivation(tree, tokens, mode="Leftmost")
        
        # Verify required top-level fields
        required_keys = [
            "grammar_productions",
            "start_symbol",
            "target_tokens",
            "target_string",
            "derivation_mode",
            "status",
            "success",
            "failure_reason",
            "steps",
            "ordered_sentential_forms",
            "derivation_sequence_text",
            "derivation_sequence_math",
            "terminal_yield",
            "production_history",
            "parse_tree_data"
        ]
        for key in required_keys:
            self.assertIn(key, canonical, f"Missing required key: {key}")
            
        self.assertEqual(canonical["start_symbol"], "S")
        self.assertEqual(canonical["derivation_mode"], "Leftmost")
        self.assertEqual(canonical["status"], "Accepted")
        self.assertTrue(canonical["success"])
        self.assertEqual(canonical["terminal_yield"], "(())()")
        self.assertEqual(len(canonical["ordered_sentential_forms"]), 8)

    def test_expected_derivation_sequence_text(self):
        """
        Verify the expected text derivation output for the regression test:
        S
        => (S)S
        => ((S)S)S
        => (()S)S
        => (())S
        => (())(S)S
        => (())()S
        => (())()
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input(self.target_tokens)
        trees = solver.parse(tokens)
        canonical = solver.build_canonical_derivation(trees[0], tokens, mode="Leftmost")
        
        expected_seq = (
            "S\n"
            "=> (S)S\n"
            "=> ((S)S)S\n"
            "=> (()S)S\n"
            "=> (())S\n"
            "=> (())(S)S\n"
            "=> (())()S\n"
            "=> (())()"
        )
        
        self.assertEqual(canonical["derivation_sequence_text"], expected_seq)

    def test_internal_symbol_identity_preservation(self):
        """
        Requirement 8: Preserve terminal/nonterminal identity internally,
        even if the display uses concatenated strings.
        """
        solver = CFGSolver(self.grammar, self.start_sym)
        tokens = solver.tokenize_input(self.target_tokens)
        trees = solver.parse(tokens)
        canonical = solver.build_canonical_derivation(trees[0], tokens, mode="Leftmost")
        
        steps = canonical["steps"]
        # Step 0: only nonterminal S
        self.assertEqual(len(steps[0]["sentential_symbols"]), 1)
        self.assertEqual(steps[0]["sentential_symbols"][0]["symbol"], "S")
        self.assertTrue(steps[0]["sentential_symbols"][0]["is_nonterminal"])
        self.assertIsNone(steps[0]["expanded_pos"])
        
        # Step 1: ( S ) S
        syms_1 = steps[1]["sentential_symbols"]
        self.assertEqual(len(syms_1), 4)
        self.assertFalse(syms_1[0]["is_nonterminal"]) # '('
        self.assertTrue(syms_1[1]["is_nonterminal"])  # 'S'
        self.assertFalse(syms_1[2]["is_nonterminal"]) # ')'
        self.assertTrue(syms_1[3]["is_nonterminal"])  # 'S'
        self.assertEqual(steps[1]["expanded_pos"], 0)
        
        # Final step 7: all terminals
        syms_7 = steps[7]["sentential_symbols"]
        for sym_info in syms_7:
            self.assertFalse(sym_info["is_nonterminal"])
        self.assertEqual("".join(s["symbol"] for s in syms_7), "(())()")

    def test_cross_section_consistency_regression_test(self):
        """
        Requirements 2, 3, 4, 5: Verify that every section in solve_universal
        (step-by-step, table, derivation sequence, final answer) reflects the same validated result.
        """
        data = {
            "grammar": self.grammar,
            "start_symbol": self.start_sym,
            "input_tokens": self.target_tokens,
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        self.assertIn("canonical_derivation", res)
        cd = res["canonical_derivation"]
        
        html_answer = res["subquestions"][0]["answer"]
        
        # 1. Step-by-Step explanation checks
        for s in cd["steps"]:
            if s["index"] == 0:
                self.assertIn("Start with the initial start symbol", html_answer)
                self.assertIn(s['form'], html_answer)
            else:
                self.assertIn(f"Step {s['index']}:", html_answer)
                self.assertIn(f"Expand non-terminal <strong>{s['expanded']}</strong>", html_answer)
                prod_html = s["production"].replace("->", "-&gt;")
                self.assertTrue(s["production"] in html_answer or prod_html in html_answer)
                self.assertIn(s["form"], html_answer)
                
        # 2. Derivation table checks
        self.assertIn("Sentential Form", html_answer)
        self.assertIn("Production Applied", html_answer)
        for s in cd["steps"]:
            self.assertIn(s["form"], html_answer)
            
        # 3. Derivation Sequence text checks
        expected_seq_lines = [
            "S",
            "=> (S)S",
            "=> ((S)S)S",
            "=> (()S)S",
            "=> (())S",
            "=> (())(S)S",
            "=> (())()S",
            "=> (())()"
        ]
        for line in expected_seq_lines:
            html_line = line.replace(">", "&gt;")
            self.assertTrue(line in html_answer or html_line in html_answer)
            
        # 4. Final Answer checks
        self.assertIn("Accepted.", html_answer)
        self.assertIn("The verified terminal yield is", html_answer)
        self.assertIn("(())()", html_answer)

    def test_failure_case_no_successful_derivation_table(self):
        """
        Requirement 7: If the derivation fails, do not display a successful derivation table.
        """
        data = {
            "grammar": self.grammar,
            "start_symbol": self.start_sym,
            "input_tokens": "(()",
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        cd = res["canonical_derivation"]
        self.assertFalse(cd["success"])
        self.assertEqual(cd["status"], "Rejected")
        
        html_answer = res["subquestions"][0]["answer"]
        self.assertIn("Rejected", html_answer)
        self.assertIn("No derivation table is available because the target string cannot be generated", html_answer)
        self.assertNotIn("Step 1:", html_answer)
        self.assertNotIn("Step 2:", html_answer)

    def test_frontend_and_backend_together(self):
        """
        Integration test simulating the Streamlit workflow in app.py:
        Runs solve_universal, generates HTML report, and verifies that the output file
        contains complete and mutually consistent sections.
        """
        data = {
            "grammar": self.grammar,
            "start_symbol": self.start_sym,
            "input_tokens": self.target_tokens,
            "derivation": "Leftmost"
        }
        res = solve_universal("CFG Derivation", data)
        
        output_path = "output/test_cfg_consistent_report.html"
        html_file = generate_html([res], output_path)
        self.assertTrue(os.path.exists(html_file))
        
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("Theory of Computation Answer Report", content)
        self.assertIn("AI Solution: CFG Derivation", content)
        self.assertIn("Accepted", content)
        self.assertIn("=&gt; (S)S", content)
        self.assertIn("The verified terminal yield is", content)
        self.assertIn("(())()", content)
        self.assertIn("Generated Parse Tree", content)

if __name__ == '__main__':
    unittest.main()
