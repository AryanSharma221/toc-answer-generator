import asyncio
from playwright.async_api import async_playwright

async def run_browser_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("Navigating to Streamlit app at http://localhost:8502...")
        await page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # 1. Select Mode B in sidebar
        print("Selecting Mode B: Universal Specification...")
        mode_b_label = page.locator("label:has-text('Mode B: Universal Specification')")
        await mode_b_label.click()
        await asyncio.sleep(1)

        # 2. Select CFG Solver task type
        print("Selecting CFG Solver...")
        cfg_solver_label = page.locator("label:has-text('CFG Solver')")
        await cfg_solver_label.click()
        await asyncio.sleep(2)

        # --- TEST 1: Grammar 1: S -> ( S ) S | epsilon, Target: ( ( ) ) ( ) ---
        print("Configuring Test 1: S -> ( S ) S | epsilon with target '( ( ) ) ( )'...")
        grammar_area = page.locator("textarea").first
        await grammar_area.fill("S -> ( S ) S | epsilon")

        # Fill inputs by label
        alphabet_input = page.locator("input").filter(has_text="").nth(0) # or aria-label
        # Streamlit assigns labels to inputs:
        await page.get_by_label("Alphabet (comma separated)").fill("(, )")
        await page.get_by_label("Start Symbol").fill("S")
        await page.get_by_label("Target string (space separated tokens)").fill("( ( ) ) ( )")

        # Click Generate CFG Solution button
        solve_btn = page.locator("button:has-text('Generate CFG Solution')")
        await solve_btn.click()

        print("Waiting for generation complete...")
        await page.wait_for_selector("text=Generation Complete!", timeout=25000)
        await asyncio.sleep(2)

        # Verify iframe rendered content
        frame = page.frame_locator("iframe").first
        content = await frame.locator("body").inner_html()
        
        import re
        matches = [line for line in content.splitlines() if "ambig" in line.lower() or "tree" in line.lower()]
        print("MATCHED LINES:")
        for m in matches[:10]:
            print("  ->", m.strip())

        assert "Accepted" in content, "Expected 'Accepted' in report"
        assert "(())()" in content, "Expected '(())()' terminal yield"
        assert "Generated Parse Tree 1" in content, "Expected 'Generated Parse Tree 1'"
        assert "Only 1 parse tree was found" in content, "Expected 'Only 1 parse tree was found'"
        assert "general grammar ambiguity is unproven" in content, "Expected unproven ambiguity disclaimer"
        print("Test 1 verified successfully!")

        # Screenshot Test 1
        shot1_path = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\screenshot_cfg_unambiguous_regression.png"
        await frame.locator(".cfg-solution-container").screenshot(path=shot1_path)
        print(f"Saved screenshot 1 to {shot1_path}")

        # --- TEST 2: Grammar 2: S -> S S | a, Target: a a a (Ambiguous) ---
        print("Configuring Test 2: S -> S S | a with target 'a a a'...")
        await grammar_area.fill("S -> S S | a")
        await page.get_by_label("Alphabet (comma separated)").fill("a")
        await page.get_by_label("Start Symbol").fill("S")
        await page.get_by_label("Target string (space separated tokens)").fill("a a a")

        await solve_btn.click()
        await page.wait_for_selector("text=Generation Complete!", timeout=25000)
        await asyncio.sleep(2)

        frame2 = page.frame_locator("iframe").first
        content2 = await frame2.locator("body").inner_html()

        assert "Grammar is ambiguous! Found 2 distinct parse trees" in content2, "Expected ambiguity notice"
        assert "Ambiguity Structural Difference" in content2, "Expected structural difference section"
        assert "Generated Parse Tree 1" in content2, "Expected Tree 1"
        assert "Generated Parse Tree 2" in content2, "Expected Tree 2"
        print("Test 2 verified successfully!")

        # Screenshot Test 2
        shot2_path = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\screenshot_cfg_ambiguous_two_trees.png"
        await frame2.locator(".cfg-solution-container").screenshot(path=shot2_path)
        print(f"Saved screenshot 2 to {shot2_path}")

        await browser.close()
        print("All browser verification tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_browser_verification())
