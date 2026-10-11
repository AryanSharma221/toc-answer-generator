import unittest
import re
from bs4 import BeautifulSoup
from core.universal_generator import solve_universal, to_unicode_math

class TestCFGRenderingRegression(unittest.TestCase):
    """
    Comprehensive regression test suite for CFG result rendering.
    Verifies the rendered DOM (using BeautifulSoup) across all 9 required criteria.
    """

    def setUp(self):
        # Canonical test grammar and target
        self.grammar = "S -> ( S ) S | epsilon"
        self.start_symbol = "S"
        self.target_tokens = ["(", "(", ")", ")", "(", ")"]
        self.problem_data = {
            "grammar": self.grammar,
            "start_symbol": self.start_symbol,
            "input_tokens": self.target_tokens,
            "derivation": "Leftmost"
        }

    def _get_rendered_html(self, problem_data=None):
        data = problem_data if problem_data is not None else self.problem_data
        result = solve_universal("CFG Derivation", data)
        self.assertIn("subquestions", result)
        self.assertTrue(len(result["subquestions"]) > 0)
        html = result["subquestions"][0]["answer"]
        return html

    def test_criterion_1_list_of_derivation_steps_renders_as_dom_list_items(self):
        """
        Criterion 1:
        A list of derivation steps renders as list items, not literal `<li>` strings.
        """
        html = self._get_rendered_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Must contain an ordered or unordered list in the DOM
        ol = soup.find("ol", class_="cfg-steps-list")
        self.assertIsNotNone(ol, "Expected <ol class='cfg-steps-list'> in rendered DOM")
        
        li_items = ol.find_all("li")
        self.assertGreaterEqual(len(li_items), 7, f"Expected at least 7 derivation steps, got {len(li_items)}")
        
        # Verify text of steps
        step_texts = [li.get_text() for li in li_items]
        self.assertTrue(any("Step 0" in t for t in step_texts))
        self.assertTrue(any("Step 1" in t for t in step_texts))
        
        # 2. Literal escaped tag strings MUST NOT appear in visible rendered text
        # (Exclude hidden comments)
        visible_text = soup.get_text()
        self.assertNotIn("<li>", visible_text, "Literal '<li>' tag string found in visible text")
        self.assertNotIn("</li>", visible_text, "Literal '</li>' tag string found in visible text")
        self.assertNotIn("<ul>", visible_text, "Literal '<ul>' tag string found in visible text")
        self.assertNotIn("&lt;li&gt;", visible_text, "Literal '&lt;li&gt;' entity found in visible text")
        self.assertNotIn("&lt;/li&gt;", visible_text, "Literal '&lt;/li&gt;' entity found in visible text")

    def test_criterion_2_derivation_table_renders_actual_table_rows_and_cells(self):
        """
        Criterion 2:
        A derivation table renders actual table rows and cells.
        """
        html = self._get_rendered_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Must contain an actual table element
        table = soup.find("table", class_="cfg-derivation-table")
        self.assertIsNotNone(table, "Expected <table class='cfg-derivation-table'> in rendered DOM")
        
        # 2. Must contain thead with th headers
        thead = table.find("thead")
        self.assertIsNotNone(thead, "Expected <thead> in derivation table")
        headers = [th.get_text().strip() for th in thead.find_all("th")]
        expected_headers = ["Step", "Sentential Form", "Expanded Non-terminal", "Position", "Production Applied"]
        for exp in expected_headers:
            self.assertIn(exp, headers, f"Header '{exp}' not found in table headers: {headers}")
            
        # 3. Must contain tbody with actual tr and td elements
        tbody = table.find("tbody")
        self.assertIsNotNone(tbody, "Expected <tbody> in derivation table")
        rows = tbody.find_all("tr")
        self.assertGreaterEqual(len(rows), 7, f"Expected at least 7 derivation rows, got {len(rows)}")
        
        for r in rows:
            cells = r.find_all("td")
            self.assertEqual(len(cells), 5, f"Each row should have 5 cells, got {len(cells)}")
            
        # 4. No literal table tags in visible text
        visible_text = soup.get_text()
        self.assertNotIn("<table>", visible_text, "Literal '<table>' tag string found in visible text")
        self.assertNotIn("<tr>", visible_text, "Literal '<tr>' tag string found in visible text")
        self.assertNotIn("<td>", visible_text, "Literal '<td>' tag string found in visible text")
        self.assertNotIn("&lt;table&gt;", visible_text, "Literal '&lt;table&gt;' entity found in visible text")

    def test_criterion_3_inline_grammar_productions_render_as_code(self):
        """
        Criterion 3:
        Inline grammar productions render as code.
        """
        html = self._get_rendered_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Check for code elements in DOM
        code_tags = soup.find_all("code")
        self.assertTrue(len(code_tags) > 0, "Expected <code> tags in rendered DOM")
        
        # 2. Production rules must be wrapped in code elements with cfg-prod class
        prod_codes = soup.find_all("code", class_="cfg-prod")
        self.assertTrue(len(prod_codes) > 0, "Expected <code class='cfg-prod'> elements in steps/table")
        
        # Check that production contains arrow symbol
        prod_texts = [p.get_text() for p in prod_codes]
        self.assertTrue(any("→" in t or "->" in t for t in prod_texts), f"Production rules should contain arrows: {prod_texts}")
        
        # 3. Non-terminals and symbols wrapped in code
        symbol_codes = soup.find_all("code", class_="cfg-symbol")
        self.assertTrue(len(symbol_codes) > 0, "Expected <code class='cfg-symbol'> elements")

    def test_criterion_4_math_symbols_render_correctly_no_raw_latex_or_dollars(self):
        """
        Criterion 4:
        Text containing mathematical symbols such as ⇒, ε, and ∅ renders correctly.
        No raw LaTeX commands or unnecessary dollar signs.
        """
        # Test helper function
        self.assertEqual(to_unicode_math("S -> ( S ) S | epsilon"), "S → ( S ) S | ε")
        self.assertEqual(to_unicode_math("S => (S)S"), "S ⇒ (S)S")
        self.assertEqual(to_unicode_math("A -> \\varepsilon"), "A → ε")
        self.assertEqual(to_unicode_math("$S$ -> $\\emptyset$"), "S → ∅")
        
        # Test full render output
        html = self._get_rendered_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # Derivation sequence container
        deriv_math = soup.find("div", class_="cfg-derivation-math")
        self.assertIsNotNone(deriv_math, "Expected <div class='cfg-derivation-math'>")
        math_text = deriv_math.get_text()
        self.assertIn("⇒", math_text, "Expected '⇒' derivation symbol in math block")
        self.assertIn("S", math_text)
        
        deriv_pre = soup.find("pre", class_="cfg-derivation-text")
        self.assertIsNotNone(deriv_pre, "Expected <pre class='cfg-derivation-text'>")
        self.assertIn("⇒", deriv_pre.get_text(), "Expected '⇒' in multiline derivation")
        
        # Visible text checks
        visible_text = soup.get_text()
        self.assertNotIn("\\Rightarrow", visible_text, "Raw LaTeX '\\Rightarrow' found in visible text")
        self.assertNotIn("\\varepsilon", visible_text, "Raw LaTeX '\\varepsilon' found in visible text")
        self.assertNotIn("\\emptyset", visible_text, "Raw LaTeX '\\emptyset' found in visible text")
        self.assertNotIn("\\to", visible_text, "Raw LaTeX '\\to' found in visible text")
        
        # No single dollar delimiters surrounding words in visible text ($S$, $epsilon$, etc.)
        dollar_vars = re.findall(r"\$[a-zA-Z0-9_]+\$", visible_text)
        self.assertEqual(dollar_vars, [], f"Unnecessary dollar signs found around variables: {dollar_vars}")

    def test_criterion_5_plain_text_with_angle_brackets_not_interpreted_as_html(self):
        """
        Criterion 5:
        Plain text containing angle brackets is not accidentally interpreted as HTML.
        """
        custom_data = {
            "grammar": "S -> '<tag>' S '</tag>' | 'a'",
            "start_symbol": "S",
            "input_tokens": ["<tag>", "a", "</tag>"],
            "derivation": "Leftmost"
        }
        html = self._get_rendered_html(custom_data)
        soup = BeautifulSoup(html, "html.parser")
        
        # DOM must NOT have created custom tag elements like <tag>
        self.assertIsNone(soup.find("tag"), "DOM incorrectly created a <tag> element from plain text")
        
        # But the literal text '<tag>' and '</tag>' must be present and readable inside code elements/text
        text_content = soup.get_text()
        self.assertIn("<tag>", text_content, "Plain text '<tag>' should be preserved in content")
        self.assertIn("</tag>", text_content, "Plain text '</tag>' should be preserved in content")

    def test_criterion_6_scripts_and_malicious_content_cannot_execute(self):
        """
        Criterion 6:
        AI-generated or user-provided content cannot inject executable HTML or scripts.
        """
        xss_data = {
            "grammar": "S -> a | <script>alert('xss')</script> | <img src=x onerror=alert(1)>",
            "start_symbol": "S",
            "input_tokens": ["a"],
            "derivation": "Leftmost"
        }
        html = self._get_rendered_html(xss_data)
        soup = BeautifulSoup(html, "html.parser")
        
        # Check that no script tag containing alert exists in the DOM
        for script in soup.find_all("script"):
            script_text = script.get_text()
            self.assertNotIn("alert('xss')", script_text, "Injected script alert found in executable script tag!")
            self.assertNotIn("alert(1)", script_text, "Injected script alert found in executable script tag!")
            
        # Check that no elements have onerror handler
        for el in soup.find_all(attrs={"onerror": True}):
            self.fail(f"Malicious onerror attribute found on element: {el}")

    def test_criterion_7_empty_or_malformed_sections_fail_gracefully(self):
        """
        Criterion 7:
        Empty or malformed result sections fail gracefully.
        """
        # 1. Grammar that does not cover target tokens
        uncovered_data = {
            "grammar": "S -> a S | b",
            "start_symbol": "S",
            "input_tokens": ["c", "d"],
            "derivation": "Leftmost"
        }
        html_uncovered = self._get_rendered_html(uncovered_data)
        soup_uncovered = BeautifulSoup(html_uncovered, "html.parser")
        
        # Must render Rejected badge gracefully
        badge = soup_uncovered.find("span", class_="cfg-badge-danger")
        self.assertIsNotNone(badge, "Expected Rejected badge on rejected input")
        self.assertIn("Rejected", badge.get_text())
        # Should not crash and should render sections
        self.assertTrue(len(soup_uncovered.find_all("section")) >= 2)
        
        # 2. String not generated by grammar
        invalid_str_data = {
            "grammar": "S -> a S b | epsilon",
            "start_symbol": "S",
            "input_tokens": ["a", "a", "b"],
            "derivation": "Leftmost"
        }
        html_invalid = self._get_rendered_html(invalid_str_data)
        soup_invalid = BeautifulSoup(html_invalid, "html.parser")
        badge_inv = soup_invalid.find("span", class_="cfg-badge-danger")
        self.assertIsNotNone(badge_inv)
        self.assertIn("Rejected", soup_invalid.get_text())
        
        # 3. Empty input string (epsilon test)
        empty_str_data = {
            "grammar": "S -> a S b | epsilon",
            "start_symbol": "S",
            "input_tokens": [],
            "derivation": "Leftmost"
        }
        html_empty = self._get_rendered_html(empty_str_data)
        soup_empty = BeautifulSoup(html_empty, "html.parser")
        badge_emp = soup_empty.find("span", class_="cfg-badge-success")
        self.assertIsNotNone(badge_emp, "Epsilon derivation should succeed and display Accepted badge")

    def test_criterion_8_both_light_and_dark_themes_readable(self):
        """
        Criterion 8:
        Both light and dark themes remain readable (contrast styles properly defined).
        """
        html = self._get_rendered_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # Style tag must be present
        style = soup.find("style")
        self.assertIsNotNone(style, "Expected <style> block defining CSS theme variables")
        css_text = style.get_text()
        
        # Check light mode custom properties (:root)
        self.assertIn(":root", css_text)
        self.assertIn("--cfg-bg:", css_text)
        self.assertIn("--cfg-text:", css_text)
        self.assertIn("--cfg-code-bg:", css_text)
        self.assertIn("--cfg-table-header-bg:", css_text)
        
        # Check dark mode media query
        self.assertIn("@media (prefers-color-scheme: dark)", css_text)
        
        # Verify text color vs bg color contrast in dark mode
        # In dark mode, text should be light (#f8fafc / #e2e8f0) and bg should be dark (#0f172a / #1e293b)
        self.assertIn("--cfg-bg: #0f172a;", css_text)
        self.assertIn("--cfg-text: #f8fafc;", css_text)
        self.assertIn("--cfg-code-bg: #1e293b;", css_text)
        
        # Pre and table elements must inherit or use var(--cfg-text)
        self.assertIn("color: var(--cfg-text);", css_text)
        self.assertIn("background-color: var(--cfg-code-bg);", css_text)

    def test_criterion_9_parse_tree_renderer_and_zoom_controls_functional(self):
        """
        Criterion 9:
        The parse-tree renderer and zoom controls remain functional.
        """
        html = self._get_rendered_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Figure with parse tree image must exist
        figure = soup.find("figure")
        self.assertIsNotNone(figure, "Expected <figure> element for parse tree")
        img = figure.find("img")
        self.assertIsNotNone(img, "Expected <img> element inside parse tree figure")
        img_src = img.get("src", "")
        self.assertTrue(img_src.startswith("data:image/png;base64,"), "Parse tree should have base64 PNG data")
        
        # 2. Zoom controls must exist
        buttons = figure.find_all("button")
        button_texts = [b.get_text().strip() for b in buttons]
        self.assertIn("Fit", button_texts, "Fit zoom control button missing")
        self.assertTrue(any("Zoom In" in t for t in button_texts), "Zoom In control button missing")
        self.assertTrue(any("Zoom Out" in t for t in button_texts), "Zoom Out control button missing")
        self.assertIn("Reset", button_texts, "Reset zoom control button missing")
        
        # 3. Zoom script function must be defined
        scripts = soup.find_all("script")
        zoom_script_found = any("zoom_img" in s.get_text() for s in scripts)
        self.assertTrue(zoom_script_found, "window.zoom_img JavaScript function missing from rendered output")


if __name__ == "__main__":
    unittest.main()
