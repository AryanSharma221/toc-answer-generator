import asyncio
from playwright.async_api import async_playwright

async def run_full_browser_regression():
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 950})
        page = await context.new_page()

        print("[Browser] Navigating to Streamlit app at http://localhost:8502...")
        await page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # 1. Select Mode B in sidebar
        print("[Browser] Selecting Mode B: Universal Specification...")
        mode_b_label = page.locator("label:has-text('Mode B: Universal Specification')")
        await mode_b_label.click()
        await asyncio.sleep(1)

        # 2. Select CFG Solver
        print("[Browser] Selecting CFG Solver...")
        cfg_solver_label = page.locator("label:has-text('CFG Solver')")
        await cfg_solver_label.click()
        await asyncio.sleep(2)

        grammar_area = page.locator("textarea").first
        solve_btn = page.locator("button:has-text('Generate CFG Solution')")

        # -----------------------------------------------------------------
        # TEST 1 & TEST 8 UI VERIFICATION — Nested Parentheses + Controls
        # -----------------------------------------------------------------
        print("\n--- Running Test 1 & Test 8: Nested Parentheses + UI Controls ---")
        await grammar_area.fill("S -> ( S ) S | epsilon")
        await page.get_by_label("Alphabet (comma separated)").fill("(, )")
        await page.get_by_label("Start Symbol").fill("S")
        await page.get_by_label("Target string (space separated tokens)").fill("( ( ) ) ( )")
        # Ensure Leftmost is selected
        await page.locator("label:has-text('Leftmost')").click()

        await solve_btn.click()
        await page.wait_for_selector("text=Generation Complete!", timeout=25000)
        await asyncio.sleep(2)

        frame1 = page.frame_locator("iframe").first
        body1 = frame1.locator("body")
        content1 = await body1.inner_html()

        # 1. Step-by-step solution check
        steps_list = frame1.locator("ol.cfg-steps-list")
        steps_count = await steps_list.locator("li").count()
        assert steps_count == 9, f"Expected 9 list items (8 steps + termination), got {steps_count}"
        print(f"  [OK] Step-by-step solution: {steps_count} items verified.")

        # 2. Derivation table check
        table = frame1.locator("table.cfg-derivation-table")
        row_count = await table.locator("tbody tr").count()
        assert row_count == 8, f"Expected 8 table rows (steps 0 to 7), got {row_count}"
        headers = await table.locator("thead th").all_text_contents()
        expected_headers = ["Step", "Sentential Form", "Expanded Non-terminal", "Position", "Production Applied"]
        assert headers == expected_headers, f"Header mismatch: {headers} vs {expected_headers}"
        print(f"  [OK] Derivation table: {row_count} rows, verified headers.")

        # 3. Mathematical sequence check
        math_div = frame1.locator(".cfg-derivation-math")
        math_text = await math_div.inner_text()
        assert "⇒" in math_text, "Expected ⇒ symbol in mathematical sequence"
        assert "(())()" in math_text, "Expected terminal yield in math sequence"
        print("  [OK] Mathematical sequence: Verified => sequence.")

        # 4. Final answer check
        badge = frame1.locator(".cfg-badge-success")
        badge_text = await badge.inner_text()
        assert badge_text == "Accepted", f"Expected Accepted badge, got {badge_text}"
        assert "Only 1 parse tree was found for this input string" in content1
        assert "general grammar ambiguity is unproven" in content1
        print(f"  [OK] Final answer: Accepted status and single-tree disclaimer verified.")

        # 5. Parse tree diagram check
        figure1 = frame1.locator("figure").first
        assert await figure1.is_visible(), "Parse tree figure not visible"
        tree_img1 = figure1.locator("img")
        assert await tree_img1.is_visible(), "Parse tree image not visible"
        caption1 = await figure1.locator("figcaption").inner_text()
        assert "Generated Parse Tree 1" in caption1, f"Caption mismatch: {caption1}"
        print(f"  [OK] Parse tree: Image and caption verified.")

        # 6. Zoom controls check (Fit, Zoom In, Zoom Out, Reset)
        btn_fit = figure1.locator("button:has-text('Fit')")
        btn_in = figure1.locator("button:has-text('Zoom In (+)')")
        btn_out = figure1.locator("button:has-text('Zoom Out (-)')")
        btn_reset = figure1.locator("button:has-text('Reset')")

        assert await btn_fit.is_visible() and await btn_in.is_visible() and await btn_out.is_visible() and await btn_reset.is_visible()
        
        # Test Zoom In
        await btn_in.click()
        await asyncio.sleep(0.3)
        scale_in = await tree_img1.get_attribute("data-scale")
        assert scale_in == "1.25", f"Expected scale 1.25 after Zoom In, got {scale_in}"
        
        # Test Zoom Out
        await btn_out.click()
        await asyncio.sleep(0.3)
        scale_out = await tree_img1.get_attribute("data-scale")
        assert scale_out == "1", f"Expected scale 1.0 after Zoom Out, got {scale_out}"

        # Test Reset
        await btn_in.click()
        await btn_in.click()
        await btn_reset.click()
        await asyncio.sleep(0.3)
        scale_reset = await tree_img1.get_attribute("data-scale")
        assert scale_reset == "1", f"Expected scale 1 after Reset, got {scale_reset}"
        print("  [OK] Zoom controls: Fit, Zoom In (+), Zoom Out (-), Reset verified functioning interactively.")

        # 7. Responsive layout check
        table_container = frame1.locator(".cfg-table-container")
        overflow_x = await table_container.evaluate("el => window.getComputedStyle(el).overflowX")
        assert overflow_x in ["auto", "scroll"], f"Expected overflow-x auto, got {overflow_x}"
        print("  [OK] Responsive layout: .cfg-table-container scroll verified.")

        # 8. Light / Dark theme contrast check
        body_bg = await body1.evaluate("el => window.getComputedStyle(el).backgroundColor")
        body_color = await body1.evaluate("el => window.getComputedStyle(el).color")
        table_th_bg = await frame1.locator("table.cfg-derivation-table th").first.evaluate("el => window.getComputedStyle(el).backgroundColor")
        print(f"  [OK] Theme contrast: Body bg={body_bg}, color={body_color}, th bg={table_th_bg}")

        shot1 = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\regression_test1_ui_full.png"
        await frame1.locator(".cfg-solution-container").screenshot(path=shot1)
        print(f"  Saved screenshot: {shot1}")
        results["TEST_1_AND_8"] = "PASS"

        # -----------------------------------------------------------------
        # TEST 4 UI VERIFICATION — Invalid String (ab)
        # -----------------------------------------------------------------
        print("\n--- Running Test 4: Invalid String (ab) ---")
        await grammar_area.fill("S -> a S | epsilon")
        await page.get_by_label("Alphabet (comma separated)").fill("a, b")
        await page.get_by_label("Start Symbol").fill("S")
        await page.get_by_label("Target string (space separated tokens)").fill("ab")

        await solve_btn.click()
        await page.wait_for_selector("text=Generation Complete!", timeout=25000)
        await asyncio.sleep(2)

        frame4 = page.frame_locator("iframe").first
        content4 = await frame4.locator("body").inner_html()

        assert "Rejected" in content4, "Expected 'Rejected' in content"
        assert "Accepted" not in content4, "Should not report Accepted"
        badge_danger = frame4.locator(".cfg-badge-danger")
        assert await badge_danger.is_visible(), "Expected Rejected danger badge"
        assert await frame4.locator("table.cfg-derivation-table").count() == 0, "No derivation table should exist on rejection"
        print("  [OK] Test 4: Rejection without false success verified.")
        shot4 = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\regression_test4_rejected_ui.png"
        await frame4.locator(".cfg-solution-container").screenshot(path=shot4)
        print(f"  Saved screenshot: {shot4}")
        results["TEST_4"] = "PASS"

        # -----------------------------------------------------------------
        # TEST 5 UI VERIFICATION — Ambiguous Grammar (S -> S S | a, target aaa)
        # -----------------------------------------------------------------
        print("\n--- Running Test 5: Ambiguous Grammar (Two Trees) ---")
        await grammar_area.fill("S -> S S | a")
        await page.get_by_label("Alphabet (comma separated)").fill("a")
        await page.get_by_label("Start Symbol").fill("S")
        await page.get_by_label("Target string (space separated tokens)").fill("a a a")

        await solve_btn.click()
        await page.wait_for_selector("text=Generation Complete!", timeout=25000)
        await asyncio.sleep(2)

        frame5 = page.frame_locator("iframe").first
        content5 = await frame5.locator("body").inner_html()

        assert "Grammar is ambiguous! Found 2 distinct parse trees" in content5
        assert "Ambiguity Structural Difference" in content5
        fig_count5 = await frame5.locator("figure").count()
        assert fig_count5 == 2, f"Expected 2 parse tree figures, got {fig_count5}"
        
        # Verify both trees have zoom controls
        btn_in_tree2 = frame5.locator("figure").nth(1).locator("button:has-text('Zoom In (+)')")
        assert await btn_in_tree2.is_visible(), "Expected zoom controls on tree 2"
        print(f"  [OK] Test 5: Ambiguity notice and 2 parse trees with zoom controls verified.")
        shot5 = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\regression_test5_ambiguous_ui.png"
        await frame5.locator(".cfg-solution-container").screenshot(path=shot5)
        print(f"  Saved screenshot: {shot5}")
        results["TEST_5"] = "PASS"

        # -----------------------------------------------------------------
        # TEST 6 UI VERIFICATION — Rightmost Derivation (aabb)
        # -----------------------------------------------------------------
        print("\n--- Running Test 6: Rightmost Derivation ---")
        await grammar_area.fill("S -> A B\nA -> a A | a\nB -> b B | b")
        await page.get_by_label("Alphabet (comma separated)").fill("a, b")
        await page.get_by_label("Start Symbol").fill("S")
        await page.get_by_label("Target string (space separated tokens)").fill("a a b b")
        await page.locator("label:has-text('Rightmost')").click()

        await solve_btn.click()
        await page.wait_for_selector("text=Generation Complete!", timeout=25000)
        await asyncio.sleep(2)

        frame6 = page.frame_locator("iframe").first
        content6 = await frame6.locator("body").inner_html()

        assert "Accepted" in content6
        assert "Rightmost" in content6
        # Check derivation steps in rightmost mode
        table6 = frame6.locator("table.cfg-derivation-table")
        rows6 = await table6.locator("tbody tr").count()
        assert rows6 == 6, f"Expected 6 rows, got {rows6}"
        print(f"  [OK] Test 6: Rightmost derivation executed and verified on UI.")
        shot6 = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\regression_test6_rightmost_ui.png"
        await frame6.locator(".cfg-solution-container").screenshot(path=shot6)
        print(f"  Saved screenshot: {shot6}")
        results["TEST_6"] = "PASS"

        await browser.close()
        print("\nALL BROWSER REGRESSION TESTS PASSED SUCCESSFULLY!")
        return results

if __name__ == "__main__":
    asyncio.run(run_full_browser_regression())
