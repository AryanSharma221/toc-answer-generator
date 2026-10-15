"""
Generator script for TOC_Project_Deep_Dive_and_Design_Decisions.docx
Generates an exhaustive technical deep-dive and design rationale guide for
the user and their teammate, detailing how everything works under the hood
and why specific models, algorithms, and features were chosen.
Author: Aryan Sharma (GitHub: @AryanSharma221)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# --- Color Constants ---
COLOR_PRIMARY = RGBColor(15, 44, 89)      # Deep Navy
COLOR_SECONDARY = RGBColor(30, 64, 175)   # Slate Blue
COLOR_TEXT = RGBColor(31, 41, 55)         # Charcoal Dark
COLOR_MUTED = RGBColor(107, 114, 128)     # Muted Slate
COLOR_SUCCESS = RGBColor(5, 150, 105)     # Emerald Green
COLOR_WARNING = RGBColor(217, 119, 6)     # Amber
COLOR_ERROR = RGBColor(220, 38, 38)       # Crimson

HEX_PRIMARY = "0F2C59"
HEX_SECONDARY = "1E40AF"
HEX_LIGHT_BG = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_CALLOUT_INFO_BG = "EFF6FF"
HEX_CALLOUT_INFO_BORDER = "3B82F6"
HEX_CALLOUT_WARN_BG = "FFFBEB"
HEX_CALLOUT_WARN_BORDER = "F59E0B"
HEX_CALLOUT_SUCCESS_BG = "ECFDF5"
HEX_CALLOUT_SUCCESS_BORDER = "10B981"

FONT_MAIN = "Segoe UI"
FONT_CODE = "Consolas"

def create_document():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
    return doc

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    borders_elm = ['<w:tcBorders ' + nsdecls('w') + '>']
    for side in ['top', 'left', 'bottom', 'right']:
        if side in kwargs:
            cfg = kwargs[side]
            borders_elm.append(f'<w:{side} w:val="{cfg.get("val", "single")}" w:sz="{cfg.get("sz", "8")}" w:space="{cfg.get("space", "0")}" w:color="{cfg.get("color", HEX_BORDER)}"/>')
        else:
            borders_elm.append(f'<w:{side} w:val="none"/>')
    borders_elm.append('</w:tcBorders>')
    tcPr.append(parse_xml(''.join(borders_elm)))

def add_header(doc, text, level):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = FONT_MAIN
    run.bold = True
    
    if level == 1:
        run.font.size = Pt(17)
        run.font.color.rgb = COLOR_PRIMARY
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="{HEX_SECONDARY}"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_SECONDARY
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_PRIMARY
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
    return p

def add_p(doc, text="", bold_prefix="", space_after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = FONT_MAIN
        r_pre.font.size = Pt(10)
        r_pre.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    if text:
        r = p.add_run(text)
        r.font.name = FONT_MAIN
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT
    return p

def add_bullet_p(doc, text="", bold_prefix="", level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = FONT_MAIN
        r_pre.font.size = Pt(10)
        r_pre.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    if text:
        r = p.add_run(text)
        r.font.name = FONT_MAIN
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT
    return p

def add_callout_box(doc, text, title="DESIGN PRINCIPLE", box_type="info"):
    bg_hex = HEX_CALLOUT_INFO_BG
    border_hex = HEX_CALLOUT_INFO_BORDER
    title_color = COLOR_SECONDARY
    
    if box_type == "warning":
        bg_hex = HEX_CALLOUT_WARN_BG
        border_hex = HEX_CALLOUT_WARN_BORDER
        title_color = COLOR_WARNING
    elif box_type == "success":
        bg_hex = HEX_CALLOUT_SUCCESS_BG
        border_hex = HEX_CALLOUT_SUCCESS_BORDER
        title_color = COLOR_SUCCESS

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    set_cell_border(cell, 
                    left=dict(val='single', sz='24', color=border_hex),
                    top=dict(val='single', sz='4', color=HEX_BORDER),
                    right=dict(val='single', sz='4', color=HEX_BORDER),
                    bottom=dict(val='single', sz='4', color=HEX_BORDER))
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    r_title = p.add_run(f"[{title}] ")
    r_title.font.name = FONT_MAIN
    r_title.font.size = Pt(9.5)
    r_title.bold = True
    r_title.font.color.rgb = title_color
    
    r_body = p.add_run(text)
    r_body.font.name = FONT_MAIN
    r_body.font.size = Pt(9.5)
    r_body.font.color.rgb = COLOR_TEXT
    
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    set_cell_border(cell, 
                    left=dict(val='single', sz='12', color='94A3B8'),
                    top=dict(val='single', sz='4', color='CBD5E1'),
                    right=dict(val='single', sz='4', color='CBD5E1'),
                    bottom=dict(val='single', sz='4', color='CBD5E1'))
    
    lines = code_str.strip().split('\n')
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.05
        r = p.add_run(line)
        r.font.name = FONT_CODE
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(15, 23, 42)
        
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(4)

def add_table_data(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        cell = hdr_cells[i]
        if col_widths and i < len(col_widths):
            cell.width = Inches(col_widths[i])
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        set_cell_border(cell, 
                        top=dict(val='single', sz='8', color=HEX_PRIMARY),
                        bottom=dict(val='single', sz='12', color=HEX_SECONDARY),
                        left=dict(val='single', sz='4', color='334155'),
                        right=dict(val='single', sz='4', color='334155'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = FONT_MAIN
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    trPr = tbl.rows[0]._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for r_idx, row_data in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_col = HEX_LIGHT_BG if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row_cells[c_idx]
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_cell_border(cell, 
                            top=dict(val='single', sz='4', color=HEX_BORDER),
                            bottom=dict(val='single', sz='4', color=HEX_BORDER),
                            left=dict(val='single', sz='4', color=HEX_BORDER),
                            right=dict(val='single', sz='4', color=HEX_BORDER))
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(val))
            r.font.name = FONT_MAIN
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_TEXT
            
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(6)

print("Base definitions ready for deep dive generator.")

def build_full_deep_dive_document():
    doc = create_document()
    
    # ---------------------------------------------------------------------------
    # DOCUMENT HEADER / TITLE BLOCK
    # ---------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    r_title = title_p.add_run("THEORY OF COMPUTATION WORKBENCH: TECHNICAL DEEP DIVE & DESIGN DECISIONS")
    r_title.font.name = FONT_MAIN
    r_title.font.size = Pt(21)
    r_title.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY
    
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    r_sub = sub_p.add_run("A Teammate's Comprehensive Guide: How Everything Works Under the Hood, Why Specific Models & Features Were Chosen, and Underlying Theoretical Foundations")
    r_sub.font.name = FONT_MAIN
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = COLOR_SECONDARY
    
    # Metadata Table
    meta_headers = ["Document Author", "GitHub Repository", "Document Target", "Release Version"]
    meta_rows = [
        ["Aryan Sharma", "github.com/AryanSharma221/toc-answer-generator", "Internal Teammate Deep-Dive & Project Defense", "v2.4 Production Release"]
    ]
    add_table_data(doc, meta_headers, meta_rows, col_widths=[1.5, 2.2, 1.8, 1.0])

    add_callout_box(
        doc,
        "Welcome to the internal engineering guide for our Theory of Computation workbench. "
        "This document is written specifically for you and our development team. It demystifies every algorithm, "
        "explains the non-obvious engineering decisions behind our tech stack, breaks down our zero-hallucination policy, "
        "and equips you with the theoretical proofs needed to defend this project during evaluations or technical interviews.",
        title="TEAMMATE ONBOARDING NOTE",
        box_type="info"
    )

    # ---------------------------------------------------------------------------
    # SECTION 1: THE CORE PHILOSOPHY
    # ---------------------------------------------------------------------------
    add_header(doc, "1. The Core Philosophy: Why We Can't Just 'Prompt an LLM' for TOC", level=1)
    
    add_p(doc,
          "When approaching an automated Theory of Computation (TOC) solver, the most tempting initial instinct is simply "
          "to pipe the user's grammar or state machine into an LLM with a prompt like: 'Minimize this DFA' or 'Derive this string "
          "using leftmost derivation.'",
          bold_prefix="The Naive Temptation: ")

    add_p(doc,
          "In practice, this approach fails catastrophically. Theory of Computation is built upon absolute mathematical invariants: "
          "state transition functions are deterministic mappings delta: Q x Sigma -> Q, language equivalence L(M1) == L(M2) requires "
          "isomorphism of minimum quotients, and context-free derivations require strict formal frontier substitution. "
          "LLMs, on the other hand, are probabilistic next-token predictors. They have no internal state registers, cannot execute "
          "discrete graph traversals without accumulated error, and cannot guarantee mathematical termination.",
          bold_prefix="The Fundamental Mismatch: ")

    add_p(doc, "During our early development and stress-testing, pure LLM prompting exhibited five fatal failure modes:")
    
    failure_headers = ["Failure Mode", "Observed LLM Hallucination", "Why It Happens in Autoregressive Models", "Our System's Deterministic Defense"]
    failure_rows = [
        ["1. Derivation Step Skipping", "Skipped non-terminals, jumping from S => (S)S directly to (())() in 3 steps instead of 7.", "Attention mechanisms prioritize overall semantic similarity over strict step-by-step frontier substitution.", "EarleyChartParser generates the exact syntax tree; get_detailed_derivation() simulates each frontier replacement deterministically."],
        ["2. Epsilon Confusion", "Emitted literal strings like '(())epsilon' or treated 'eps' as an output token in the final string.", "The model confuses the meta-linguistic symbol ε with a literal output character.", "CFGSolver normalizes ε into empty transitions; frontier rendering deletes the nonterminal without emitting output tokens."],
        ["3. Spurious State Merges", "Merged an accepting state and a non-accepting state into the same minimized equivalence class.", "The LLM groups states based on naming similarity or semantic proximity rather than distinguishability.", "ValidationGate asserts that no equivalence class ever mixes accepting and non-accepting states; otherwise raises ValueError."],
        ["4. False Acceptance Claims", "Reported 'Accepted' for an invalid target string merely because it found a partial derivation.", "Autoregressive generation loses track of string length and terminates prematurely with an agreeable tone.", "validate_derivation() asserts that the leaf yield of the derivation tree equals the target token array with 100% precision."],
        ["5. Unchecked Ambiguity", "Declared a grammar unambiguous because it only generated one tree, or claimed ambiguity without proof.", "LLMs cannot exhaustively verify the tree search space and fabricate speculative ambiguity claims.", "Chart parser exhaustively searches all trees; if tree_count > 1, pinpoints pre-order divergence; if 1, emits unproven disclaimer."]
    ]
    add_table_data(doc, failure_headers, failure_rows, col_widths=[1.3, 1.7, 1.8, 1.7])

    add_callout_box(
        doc,
        "OUR CARDINAL RULE: 'Deterministic Truth, LLM Explanation'.\n"
        "1. Deterministic algorithms (NLTK Earley parsing, Myhill-Nerode table filling, BFS reachability, subset construction) compute the 100% verified mathematical result.\n"
        "2. The LLM is fed the verified 'canonical_result' and is strictly forbidden from recalculating the math. Its sole job is to provide clean, pedagogical explanations.",
        title="THE GOLDEN ARCHITECTURAL RULE",
        box_type="success"
    )

    # ---------------------------------------------------------------------------
    # SECTION 2: WHY WE USED SPECIFIC MODELS AND LIBRARIES
    # ---------------------------------------------------------------------------
    add_header(doc, "2. Why We Used Specific Models & Libraries (The 'Why' Behind Every Choice)", level=1)

    add_p(doc, "Every dependency and model in our requirements.txt was selected deliberately to solve a specific engineering bottleneck:")

    # 2.1 Gemini
    add_header(doc, "2.1 Why Google Gemini (gemini-3.5-flash-lite / Gemini Flash Family)", level=2)
    add_p(doc,
          "We chose Google Gemini's flash-tier models (specifically gemini-3.5-flash-lite) over heavier models (like GPT-4o or Gemini Pro) "
          "for three strategic reasons:",
          bold_prefix="Model Selection Rationale: ")
    add_bullet_p(doc, "Sub-Second Latency: In an interactive Streamlit UI, users cannot wait 15–30 seconds for heavy reasoning models. Flash-lite provides sub-second response times, making UI generation feel instantaneous.", bold_prefix="1. Speed: ")
    add_bullet_p(doc, "Strict JSON Schema Mode: Gemini natively supports response_mime_type: 'application/json'. This guarantees that the model outputs clean, parseable JSON without hallucinating markdown blocks (```json) that break Python json.loads().", bold_prefix="2. Reliable JSON: ")
    add_bullet_p(doc, "Cost-Effectiveness & API Quota: Generating rich 6-section explanations across multiple test cases burns tokens rapidly. Flash models provide optimal pedagogical fluency at a fraction of the token cost.", bold_prefix="3. Resource Efficiency: ")

    # 2.2 KeyManager
    add_header(doc, "2.2 Why Multi-Key Dynamic Rotation (KeyManager)", level=2)
    add_p(doc,
          "During live demos, automated test runs, and continuous integration, developer API keys inevitably encounter "
          "HTTP 429 Too Many Requests errors or daily quota exhaustion.",
          bold_prefix="The Problem: ")
    add_p(doc,
          "We engineered the KeyManager class in core/ai_integration.py. It automatically parses comma-separated keys from "
          "GEMINI_API_KEYS or numbered variables GEMINI_API_KEY_1..N. When an API call catches a 429 quota exception, it logs "
          "the event, increments the key index, and retries the request transparently. Furthermore, if all keys expire or the user "
          "has no internet connection, the system gracefully degrades: it bypasses the LLM and renders the verified deterministic "
          "math directly. The app NEVER crashes due to an API outage.",
          bold_prefix="The Solution: ")

    # 2.3 NLTK Earley Parser
    add_header(doc, "2.3 Why NLTK EarleyChartParser for Context-Free Grammars", level=2)
    add_p(doc,
          "Choosing the parsing engine was one of our most critical decisions. Why didn't we write a recursive-descent parser "
          "or use standard LL(1) / LR(1) parser generators?",
          bold_prefix="Parser Dilemma: ")
    add_bullet_p(doc, "The Left-Recursion Death Trap: Many classical grammars in TOC (e.g. S -> S S | a or E -> E + T) are immediately left-recursive. Recursive descent parsers enter infinite recursion and crash with RecursionError.", bold_prefix="Why NOT Recursive Descent: ")
    add_bullet_p(doc, "Grammar Restriction Inflexibility: LL(1) and LR(1) parsers require grammars to be transformed into strict deterministic forms (eliminating left recursion, left factoring, resolving shift-reduce conflicts). Students and educators input natural, textbook grammars that violate these restrictions.", bold_prefix="Why NOT LL/LR: ")
    add_bullet_p(doc, "Earley Chart Parsing (The Perfect Fit): Earley's algorithm uses dynamic programming with state sets. It handles ANY context-free grammar—including left-recursive, right-recursive, ambiguous, and epsilon grammars—in O(n³) worst-case and O(n) for unambiguous grammars. Crucially, it explores all derivation paths simultaneously, allowing us to discover multiple parse trees for ambiguity proofs!", bold_prefix="Why Earley Chart Parsing: ")

    # 2.4 automata-lib
    add_header(doc, "2.4 Why automata-lib", level=2)
    add_p(doc,
          "We integrated automata-lib as our formal independent mathematical reference oracle. When our custom DFAMinimizer "
          "produces a minimized DFA, we construct independent automata-lib DFA instances for both the original and minimized "
          "automata. We then execute dfa_expected == dfa_actual. Under the hood, this computes the symmetric difference (DFA1 XOR DFA2) "
          "and asserts that its language is empty (L == ∅). This mathematically proves that our minimization preserved the exact language.",
          bold_prefix="Independent Mathematical Oracle: ")

    # 2.5 Graphviz
    add_header(doc, "2.5 Why Graphviz (DOT Engine)", level=2)
    add_p(doc,
          "Graph visualization in formal languages requires specialized layout rules: initial states must have free incoming arrows, "
          "accepting states require concentric double circles, and parse trees must be hierarchically balanced. Hand-rolling SVG coordinates "
          "leads to overlapping text and unreadable edge crossings. Graphviz's dot engine uses spring-electrical and hierarchical ranking "
          "algorithms that compute optimal node splines and aspect ratios automatically.",
          bold_prefix="Automated Topological Layout: ")

    # 2.6 WeasyPrint & MathJax
    add_header(doc, "2.6 Why WeasyPrint & MathJax", level=2)
    add_p(doc,
          "Academic solutions demand professional typography. MathJax v3 renders beautiful mathematical notation "
          "(Unicode arrows ⇒, Greek symbols ε, δ, transitions, and subscripts). For PDF output, traditional libraries like ReportLab "
          "require tedious coordinate math. WeasyPrint allows us to use modern CSS Paged Media (@page, page-break-inside: avoid), "
          "compiling our HTML dossier into an exam-ready PDF with pixel-perfect pagination.",
          bold_prefix="Publication-Quality Publishing: ")

    # ---------------------------------------------------------------------------
    # SECTION 3: FEATURE-BY-FEATURE DEEP DIVE
    # ---------------------------------------------------------------------------
    add_header(doc, "3. Feature-by-Feature Deep Dive: How Everything Works Under the Hood", level=1)

    # 3.1 CFG Tokenization
    add_header(doc, "3.1 Feature 1: CFG Input Tokenization & Grammar Normalization", level=2)
    add_p(doc,
          "The Problem: Students typically input target strings with visual space separators, e.g., '( ( ) ) ( )'. "
          "Naive parsers treat spaces as literal alphabet symbols, causing the infamous error: 'Grammar does not cover input word: ' '.' "
          "Conversely, if a grammar genuinely contains a multi-character terminal with a space (e.g. 'a b'), stripping spaces corrupts the input.",
          bold_prefix="The Whitespace Dilemma: ")
    add_p(doc,
          "How CFGSolver Solves It: In solvers/cfg_solver.py, tokenize_input() inspects the grammar's known terminals. "
          "If the grammar uses single-character terminals, all formatting whitespace is ignored, tokenizing '( ( ) ) ( )' into "
          "['(', '(', ')', ')', '(', ')'] with compact yield '(())()'. If a terminal is explicitly enclosed in single or double quotes "
          "(e.g. ''a b''), the tokenizer protects the interior space as an atomic token. Furthermore, concatenated production rules like "
          "S -> (S)S are safely split into '(' S ')' S without breaking user-defined multi-character nonterminals like 'NT'.",
          bold_prefix="The Solution: ")

    # 3.2 CFG Derivation
    add_header(doc, "3.2 Feature 2: CFG Leftmost & Rightmost Derivations", level=2)
    add_p(doc,
          "How It Works: Once the Earley parser produces a parse tree (an NLTK Tree structure), get_detailed_derivation() simulates "
          "the derivation step-by-step. It maintains a frontier list initially containing [tree].",
          bold_prefix="Frontier Simulation: ")
    add_bullet_p(doc, "Leftmost Mode: Scans the frontier from left to right (index 0 to N-1) to find the first node that is an instance of Tree (a non-terminal).", bold_prefix="Search Strategy: ")
    add_bullet_p(doc, "Rightmost Mode: Scans the frontier in reverse (index N-1 down to 0) to find the rightmost Tree instance.", bold_prefix="Search Strategy: ")
    add_bullet_p(doc, "Production Extraction: Reads the children of the non-terminal. If children is empty, the production is NonTerminal -> ε. Otherwise, NonTerminal -> Child1 Child2...", bold_prefix="Production Resolution: ")
    add_bullet_p(doc, "Frontier Replacement: Slices the frontier: frontier[:idx] + children + frontier[idx+1:].", bold_prefix="Replacement: ")
    add_bullet_p(doc, "Epsilon Elimination: When expanding to ε, children is empty ([]). Slicing naturally deletes the non-terminal from the sentential form without ever appending a literal 'epsilon' string!", bold_prefix="Epsilon Elimination: ")
    add_bullet_p(doc, "Symbol Identity Preservation: Each step records sentential_symbols: [{'symbol': 'S', 'is_nonterminal': True}, ...]. This allows downstream validation gates to verify rightmost/leftmost correctness deterministically.", bold_prefix="Invariant Recording: ")

    # 3.3 Ambiguity Analysis
    add_header(doc, "3.3 Feature 3: CFG Ambiguity Analysis & Multi-Tree Rendering", level=2)
    add_p(doc,
          "Theoretical Foundation: A Context-Free Grammar is ambiguous if and only if there exists at least one string in its language "
          "that has two or more distinct parse trees (or equivalently, two or more distinct leftmost derivations).",
          bold_prefix="Formal Definition: ")
    add_p(doc,
          "How We Prove Ambiguity: When the Earley parser executes, it collects all possible derivation trees. "
          "If tree_count > 1 (for example, grammar S -> S S | a on target 'aaa' produces 2 trees), the system:",
          bold_prefix="Ambiguity Proof: ")
    add_bullet_p(doc, "Declares the grammar formally Ambiguous with 100% mathematical certainty.", bold_prefix="1. Status: ")
    add_bullet_p(doc, "Executes explain_structural_difference(tree1, tree2): Traverses both trees simultaneously in pre-order. At the first node coordinate where tree1 has production S -> S S and tree2 has S -> a, it generates an explanation pinpointing the structural divergence.", bold_prefix="2. Structural Difference: ")
    add_bullet_p(doc, "Renders individual Graphviz parse trees for each derivation (Generated Parse Tree 1, Generated Parse Tree 2), complete with interactive zoom controls.", bold_prefix="3. Dual Visualization: ")
    
    add_callout_box(
        doc,
        "CRITICAL MATHEMATICAL NUANCE:\n"
        "If the parser discovers only 1 parse tree for an input string, our system DOES NOT claim that the grammar is unambiguous!\n"
        "Grammar ambiguity is undecidable in the general case (proven by Post's Correspondence Problem). A single tree only proves "
        "that the grammar is unambiguous for that specific input string. Our report explicitly renders: "
        "'Only 1 parse tree was found for this input string (the grammar is unambiguous for this string; general grammar ambiguity is unproven).' "
        "This level of mathematical precision prevents professors and reviewers from penalizing the solution.",
        title="MATHEMATICAL ACCURACY SAFEGUARD",
        box_type="warning"
    )

    # 3.4 DFA Minimization
    add_header(doc, "3.4 Feature 4: DFA Minimization (Myhill-Nerode Table-Filling)", level=2)
    add_p(doc,
          "How DFAMinimizer Operates Step-by-Step:",
          bold_prefix="Algorithmic Pipeline: ")
    add_bullet_p(doc, "Step 1: Reachable State Discovery. Executes BFS starting from start_state. Any state in Q not visited during BFS is identified as unreachable, reported in the diagnostic output, and purged before minimization.", bold_prefix="1. Reachability: ")
    add_bullet_p(doc, "Step 2: Initial Partition (0-Equivalence). Partitions reachable states into F (Accepting) and Q \\ F (Non-Accepting). In the triangular table, all pairs (p, q) where one is accepting and the other is non-accepting are marked with an 'X'.", bold_prefix="2. 0-Equivalence: ")
    add_bullet_p(doc, "Step 3: Iterative Distinguishability Marking. For every unmarked pair (p, q) and every symbol a in Sigma, computes p' = delta(p, a) and q' = delta(q, a). If the pair (p', q') is already marked, then (p, q) is distinguished and marked. Repeats until a full pass makes zero new marks.", bold_prefix="3. Table-Filling: ")
    add_bullet_p(doc, "Step 4: Equivalence Class Merging. Unmarked pairs represent equivalent states. The algorithm finds the connected components to form merged quotient states (e.g. '{q0,q1}').", bold_prefix="4. Quotient Synthesis: ")
    add_bullet_p(doc, "Step 5: Quotient Transition Table. Defines delta_min({p, ...}, a) = {delta(p, a), ...}. Validates that every transition maps to a valid quotient class.", bold_prefix="5. Transition Mapping: ")

    # 3.5 NFA to DFA
    add_header(doc, "3.5 Feature 5: NFA to DFA Subset Construction", level=2)
    add_p(doc,
          "How NFAConverter Operates: Starts by computing the epsilon-closure of the initial state: E(q0). This subset becomes the DFA's "
          "initial state. For each discovered subset S and each alphabet symbol 'a', it computes U = E(bigcup_{q in S} delta(q, a)). "
          "If U is empty, it routes the transition to an explicit trap state ('∅'). Any subset containing an NFA accepting state becomes "
          "a DFA accepting state. The resulting DFA transition table and subset mapping dictionary are passed to the validation gate.",
          bold_prefix="Powerset Algorithm: ")

    # 3.6 Interactive Zoom
    add_header(doc, "3.6 Feature 6: Interactive Zoom & Pan Controls", level=2)
    add_p(doc,
          "The Problem: Large parse trees and state automata have high aspect ratios. Embedded in static web pages, they either scale down "
          "until the text is microscopic or overflow awkwardly.",
          bold_prefix="The UI Challenge: ")
    add_p(doc,
          "Our Solution: In core/universal_generator.py, we inject client-side JavaScript into each diagram's <figure>. "
          "The script binds four buttons: 'Fit', 'Zoom In (+)', 'Zoom Out (-)', and 'Reset'. Scaling is manipulated directly in the DOM "
          "by updating img.style.width and tracking current scale on a custom data-scale attribute. The zooming is buttery smooth, "
          "operates entirely in the browser with zero latency, and never triggers Streamlit session refreshes.",
          bold_prefix="The Implementation: ")

    # ---------------------------------------------------------------------------
    # SECTION 4: THE TRI-LAYER VERIFICATION ARCHITECTURE
    # ---------------------------------------------------------------------------
    add_header(doc, "4. The Tri-Layer Verification Architecture: Why Our System Never Lies", level=1)

    add_p(doc,
          "To guarantee that no hallucination, edge-case bug, or algorithmic regression ever reaches the user, "
          "we designed a Tri-Layer Verification Architecture:")

    tri_headers = ["Layer", "Component", "Verification Mechanism", "Failure Action"]
    tri_rows = [
        ["Layer 1: Primary Computation", "solvers/ (CFGSolver, DFAMinimizer, NFAConverter)", "Authoritative deterministic algorithm execution (Earley parsing, Myhill-Nerode, powerset construction).", "Returns immediate syntax or resource error."],
        ["Layer 2: Formal Mathematical Gate", "core/validation_gate.py\nsolvers/dfa_verification.py", "Independent assertions: partition purity, transition closure, automata-lib language equivalence L(M1) == L(M2), Moore vs. Hopcroft cross-checks.", "Raises ValueError / RuntimeError; halts execution rather than outputting incorrect math."],
        ["Layer 3: Advisory API Audit", "core/independent_verifier.py\ncore/ai_integration.py", "Zero-context API query to Gemini asking it to solve the problem independently. Compares state counts, traces, and partitions against canonical result.", "Logs discrepancies for developer auditing; strictly overrides AI with deterministic result."]
    ]
    add_table_data(doc, tri_headers, tri_rows, col_widths=[1.3, 1.7, 2.3, 1.2])

    add_callout_box(
        doc,
        "BENEFIT FOR EVALUATORS:\n"
        "Even if someone intentionally injects a corrupted prompt or tries to trick the AI, Layer 2 (ValidationGate) will physically "
        "block the corrupted output from rendering because automata-lib will detect a language equivalence mismatch. "
        "The system has zero tolerance for mathematical error.",
        title="DEFENSE IN DEPTH",
        box_type="info"
    )

    # ---------------------------------------------------------------------------
    # SECTION 5: TEAMMATE CODE WALKTHROUGH
    # ---------------------------------------------------------------------------
    add_header(doc, "5. Teammate Code Walkthrough: Tracing Real Execution Flows", level=1)

    add_p(doc, "To help you navigate the codebase quickly, here is the exact trace of what happens when a user clicks 'Generate CFG Solution':")

    walkthrough_code = """1. app.py (Line 181):
   User clicks 'Generate CFG Solution'.
   Gathers: grammar, start_symbol, alphabet, target_string, derivation_type ('Leftmost').
   Calls: res = solve_universal('CFG Derivation', data)

2. core/universal_generator.py (Line 617):
   solve_universal receives category == 'CFG Derivation'.
   Instantiates: solver = CFGSolver(grammar, start_symbol, alphabet)
   Calls: tokens = solver.tokenize_input(raw_tokens)
   Validates tokens against alphabet.

3. solvers/cfg_solver.py (Line 115):
   Calls: trees = solver.parse(tokens)
   EarleyChartParser builds parse trees within 5.0s timeout and 300 token limit.
   Calls: steps = solver.get_detailed_derivation(tree, mode='Leftmost')
   Calls: err = solver.validate_derivation(steps, tokens, mode='Leftmost', tree=tree)
   Builds canonical_derivation dictionary containing steps, tables, trees, and ambiguity status.

4. core/universal_generator.py (Line 727):
   Renders parse trees into Graphviz DOT syntax.
   Compiles diagrams to SVG/PNG images.
   Calls render_cfg_typed_html():
     - Generates 6 structured sections with clean HTML tables and Unicode arrows (⇒, ε).
     - Injects interactive Zoom Controller JavaScript into each diagram figure.
     - Formats final Accepted/Rejected badge with unproven ambiguity disclaimer.

5. exporters/html_exporter.py & pdf_exporter.py:
   Converts all diagram file paths into base64 data URIs (data:image/png;base64,...).
   Saves standalone report to output/mode_b_cfg_report_xxxx.html.
   Calls WeasyPrint to compile vector PDF.

6. app.py (Line 207):
   Stores html_file and pdf_file in st.session_state.
   Renders HTML report inside sandboxed st.components.v1.html iframe.
   Exposes Download HTML and Download PDF buttons."""
    add_code_block(doc, walkthrough_code)

    # ---------------------------------------------------------------------------
    # SECTION 6: TEAMMATE FAQ & PROJECT DEFENSE GUIDE
    # ---------------------------------------------------------------------------
    add_header(doc, "6. Teammate FAQ, Project Defense Guide & Interview Talking Points", level=1)

    add_p(doc, "When presenting or defending this project in academic evaluations or technical interviews, use these proven talking points:")

    add_header(doc, "Q1: 'Why didn't you just build a wrapper around ChatGPT or Gemini?'", level=3)
    add_p(doc,
          "Talking Point: 'Theory of computation requires deterministic mathematical rigor. LLMs are autoregressive probability models—they "
          "suffer from catastrophic hallucinations in state minimization, skip derivation steps, confuse epsilon with literal characters, and "
          "cannot guarantee language equivalence. We designed a hybrid architecture where formal algorithms (Earley chart parsing, "
          "Myhill-Nerode table filling, BFS reachability) compute the truth, while the LLM is sandboxed strictly to generating natural pedagogical "
          "explanations. We also enforce mathematical validation gates (using automata-lib equivalence) so the system never lies.'")

    add_header(doc, "Q2: 'What is the most technically challenging part of the CFG solver?'", level=3)
    add_p(doc,
          "Talking Point: 'Handling arbitrary context-free grammars and subtle tokenization boundaries. Standard parsers either fail on left-recursive "
          "grammars or treat formatting spaces as terminals. We implemented quote-aware tokenization to preserve multi-character terminals while "
          "ignoring token separator spaces, integrated NLTK's Earley parser to safely handle left/right recursion without stack overflows, "
          "and built a pre-order tree traversal algorithm that pinpoints the exact structural node where ambiguous derivations diverge.'")

    add_header(doc, "Q3: 'How does your DFA Minimizer handle unreachable states?'", level=3)
    add_p(doc,
          "Talking Point: 'Many student implementations apply table-filling directly over all states, which produces incorrect quotient classes "
          "if unreachable states exist. Our DFAMinimizer executes a BFS from the start state to purge unreachable states first. Then it constructs "
          "the 0-equivalent partition, iterates over the distinguishability matrix until fixpoint, synthesizes composite quotient states, and "
          "validates language equivalence against automata-lib before rendering.'")

    add_header(doc, "Q4: 'What happens if Google Gemini's API goes down or hits a rate limit?'", level=3)
    add_p(doc,
          "Talking Point: 'Our system has zero dependency on third-party uptime. First, our KeyManager automatically cycles through fallback API keys "
          "on HTTP 429 errors. Second, if all keys fail or there is no network connection, our universal generator falls back to deterministic "
          "template rendering. 100% of the derivations, tables, Graphviz diagrams, and PDF exports are generated entirely on the local machine.'")

    add_callout_box(
        doc,
        "SUMMARY FOR THE TEAM:\n"
        "You now have complete mastery over the architecture, algorithms, and design rationale of our project. "
        "Feel confident walking through the codebase, running the test suites, and defending our architectural choices!",
        title="READY FOR PRESENTATION & DEFENSE",
        box_type="success"
    )

    # Save Document
    target_path = os.path.abspath("TOC_Project_Deep_Dive_and_Design_Decisions.docx")
    doc.save(target_path)
    print(f"Deep-dive document successfully created and saved at: {target_path}")
    return target_path

if __name__ == "__main__":
    build_full_deep_dive_document()
