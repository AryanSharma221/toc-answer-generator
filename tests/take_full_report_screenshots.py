import asyncio
import os
import glob
from playwright.async_api import async_playwright
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html

async def capture_full_reports():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1800})

        # Report 1: Unambiguous Regression
        data1 = {
            "grammar": "S -> ( S ) S | epsilon",
            "start_symbol": "S",
            "alphabet": "(, )",
            "input_tokens": "( ( ) ) ( )",
            "derivation": "Leftmost"
        }
        res1 = solve_universal("CFG Derivation", data1)
        html_path1 = os.path.abspath("output/report_test1_unambiguous.html")
        generate_html([res1], html_path1)

        await page.goto(f"file:///{html_path1.replace(os.sep, '/')}", wait_until="networkidle")
        await asyncio.sleep(1)
        shot1_path = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\screenshot_cfg_unambiguous_full_report.png"
        await page.screenshot(path=shot1_path, full_page=True)
        print(f"Captured full report 1: {shot1_path}")

        # Report 2: Ambiguous Multiple Trees
        data2 = {
            "grammar": "S -> S S | a",
            "start_symbol": "S",
            "alphabet": "a",
            "input_tokens": "a a a",
            "derivation": "Leftmost"
        }
        res2 = solve_universal("CFG Derivation", data2)
        html_path2 = os.path.abspath("output/report_test2_ambiguous.html")
        generate_html([res2], html_path2)

        await page.goto(f"file:///{html_path2.replace(os.sep, '/')}", wait_until="networkidle")
        await asyncio.sleep(1)
        shot2_path = r"C:\Users\Aryan\.gemini\antigravity\brain\266ec17c-f74a-42e5-8545-93a17daa34f4\screenshot_cfg_ambiguous_two_trees_full_report.png"
        await page.screenshot(path=shot2_path, full_page=True)
        print(f"Captured full report 2: {shot2_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_full_reports())
