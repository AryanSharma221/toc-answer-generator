"""
Generator script for TOC_Presentation_Slides.pptx
Generates an executive, 10-slide presentation deck with 16:9 widescreen layout,
professional styling, cards, tables, and full speaker notes on every slide.
Author: Aryan Sharma (GitHub: @AryanSharma221)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- Color Constants ---
COLOR_NAVY = RGBColor(15, 44, 89)       # #0F2C59 - Primary Header
COLOR_SLATE_BLUE = RGBColor(30, 64, 175) # #1E40AF - Secondary Accent
COLOR_CYAN = RGBColor(14, 165, 233)     # #0EA5E9 - Highlight
COLOR_DARK_TEXT = RGBColor(31, 41, 55)   # #1F2937 - Body Text
COLOR_MUTED = RGBColor(100, 116, 139)   # #64748B - Subtitles/Footers
COLOR_WHITE = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_CARD_BG = RGBColor(248, 250, 252) # #F8FAFC - Card Background
COLOR_CARD_BORDER = RGBColor(203, 213, 225) # #CBD5E1 - Border
COLOR_EMERALD = RGBColor(5, 150, 105)   # #059669 - Success
COLOR_AMBER = RGBColor(217, 119, 6)     # #D97706 - Warning

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"

def create_deck():
    prs = Presentation()
    # Configure 16:9 Widescreen (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def add_header_banner(slide, category_text, title_text):
    # Top header banner shape
    banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_NAVY
    banner.line.color.rgb = COLOR_SLATE_BLUE
    banner.line.width = Pt(1.5)

    # Category pill / tracker
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_TITLE
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_CYAN

    # Main Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.5), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

def add_footer(slide, current_slide, total_slides=10):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
    tf = footer_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"Theory of Computation Answer Generator & Formal Languages Workbench  |  Aryan Sharma (@AryanSharma221)  |  Slide {current_slide} of {total_slides}"
    p.font.name = FONT_BODY
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_MUTED

def add_card(slide, left, top, width, height, title="", title_color=COLOR_SLATE_BLUE, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    
    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = title_color
    return shape

def add_bullets_to_card(slide, left, top, width, height, bullet_items):
    tb = slide.shapes.add_textbox(left + Inches(0.2), top, width - Inches(0.4), height)
    tf = tb.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(bullet_items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8)
        p.line_spacing = 1.15
        
        if isinstance(item, tuple):
            prefix, text = item
            r_pre = p.add_run()
            r_pre.text = prefix + " "
            r_pre.font.name = FONT_BODY
            r_pre.font.size = Pt(11)
            r_pre.font.bold = True
            r_pre.font.color.rgb = COLOR_NAVY
            
            r_body = p.add_run()
            r_body.text = text
            r_body.font.name = FONT_BODY
            r_body.font.size = Pt(10.5)
            r_body.font.color.rgb = COLOR_DARK_TEXT
        else:
            r = p.add_run()
            r.text = item
            r.font.name = FONT_BODY
            r.font.size = Pt(10.5)
            r.font.color.rgb = COLOR_DARK_TEXT

def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text.strip()

print("Presentation helpers ready.")

def build_all_slides():
    prs = create_deck()
    blank_layout = prs.slide_layouts[6]
    
    # =========================================================================
    # SLIDE 1: TITLE SLIDE (COVER)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    
    # Background full color card
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_NAVY
    bg.line.fill.background()

    # Pill badge
    pill = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(4.5), Inches(0.45))
    pill.fill.solid()
    pill.fill.fore_color.rgb = COLOR_SLATE_BLUE
    pill.line.fill.background()
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "FORMAL LANGUAGES & AUTOMATA BENCHMARK"
    p_pill.font.name = FONT_TITLE
    p_pill.font.size = Pt(11)
    p_pill.font.bold = True
    p_pill.font.color.rgb = COLOR_CYAN
    p_pill.alignment = PP_ALIGN.CENTER

    # Main Title
    tb_title = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.2))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_main = tf_title.paragraphs[0]
    p_main.text = "Theory of Computation Answer Generator\n& Formal Languages Workbench"
    p_main.font.name = FONT_TITLE
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_WHITE
    p_main.space_after = Pt(14)

    # Subtitle
    p_sub = tf_title.add_paragraph()
    p_sub.text = "A Decoupled Hybrid Deterministic-Advisory Architecture for Zero-Hallucination Automata & Grammar Solving"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = RGBColor(226, 232, 240)

    # Card with author and tech stack
    add_card(slide1, Inches(1.2), Inches(4.6), Inches(10.933), Inches(1.8), 
             title="", bg_color=RGBColor(24, 38, 70), border_color=RGBColor(51, 65, 85))
    
    tb_meta = slide1.shapes.add_textbox(Inches(1.5), Inches(4.8), Inches(10.3), Inches(1.4))
    tf_meta = tb_meta.text_frame
    
    p_m1 = tf_meta.paragraphs[0]
    p_m1.text = "Presented by: Aryan Sharma (@AryanSharma221)"
    p_m1.font.name = FONT_TITLE
    p_m1.font.size = Pt(15)
    p_m1.font.bold = True
    p_m1.font.color.rgb = COLOR_WHITE
    p_m1.space_after = Pt(6)

    p_m2 = tf_meta.add_paragraph()
    p_m2.text = "Core Stack: Python 3.10+ | Streamlit | NLTK Earley Parser | Graphviz DOT | automata-lib | Google Gemini Flash | WeasyPrint"
    p_m2.font.name = FONT_BODY
    p_m2.font.size = Pt(11)
    p_m2.font.color.rgb = COLOR_CYAN
    p_m2.space_after = Pt(4)

    p_m3 = tf_meta.add_paragraph()
    p_m3.text = "Open Source Repository: https://github.com/AryanSharma221/toc-answer-generator"
    p_m3.font.name = FONT_CODE
    p_m3.font.size = Pt(10)
    p_m3.font.color.rgb = RGBColor(148, 163, 184)

    set_speaker_notes(
        slide1,
        "Welcome everyone. Today, my teammate and I are presenting our project: the Theory of Computation Answer Generator & Formal Languages Workbench.\n\n"
        "This project tackles one of the greatest unsolved challenges in AI-assisted computer science education: how to automatically generate 100% mathematically verified, step-by-step solutions for formal automata and grammars without the catastrophic hallucinations that plague modern Large Language Models.\n\n"
        "Over the next 10 slides, we will break down our core architectural philosophy, our deterministic solver engines, our tri-layer mathematical verification gate, and why we chose our specific models and features."
    )

    # =========================================================================
    # SLIDE 2: THE CORE PROBLEM
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide2, "The Problem Statement", "Why Pure LLMs Fail Catastrophically at Theory of Computation")
    add_footer(slide2, 2)

    # 3 Cards Layout
    w_card = Inches(3.64)
    h_card = Inches(5.3)
    y_card = Inches(1.45)

    # Card 1: Probabilistic Mismatch
    add_card(slide2, Inches(0.8), y_card, w_card, h_card, "1. The Fundamental Mismatch", COLOR_NAVY)
    add_bullets_to_card(slide2, Inches(0.8), y_card + Inches(0.65), w_card, h_card - Inches(0.8), [
        ("Discrete vs. Probabilistic:", "TOC relies on strict transition mappings delta: Q x Sigma -> Q and exact grammatical frontiers. LLMs predict the most statistically probable next token."),
        ("No Internal State Machine:", "Transformer attention heads possess no persistent state registers or dynamic memory cells to simulate multi-step graph traversals."),
        ("Accumulated Error Drift:", "A 1% probabilistic error in step 2 of a 7-step derivation compounds into complete mathematical nonsense by step 7.")
    ])

    # Card 2: 5 Real-World Failure Modes
    add_card(slide2, Inches(4.84), y_card, w_card, h_card, "2. Top 5 Real-World Hallucinations", COLOR_AMBER)
    add_bullets_to_card(slide2, Inches(4.84), y_card + Inches(0.65), w_card, h_card - Inches(0.8), [
        ("Step Skipping:", "Jumps over intermediate nonterminals, reducing a 7-step derivation to 3 fabricated steps."),
        ("Literal Epsilon Emission:", "Emits '(())epsilon' or treats 'eps' as a terminal character in the target string."),
        ("Spurious State Merges:", "Merges an accepting state and a non-accepting state into the same equivalence class."),
        ("False Acceptance:", "Reports 'Accepted' on invalid input strings simply because a partial path was found."),
        ("Unchecked Ambiguity:", "Claims a grammar is unambiguous without proof, or hallucinates ambiguity.")
    ])

    # Card 3: Our Engineering Mission
    add_card(slide2, Inches(8.88), y_card, w_card, h_card, "3. Our Engineering Mission", COLOR_EMERALD)
    add_bullets_to_card(slide2, Inches(8.88), y_card + Inches(0.65), w_card, h_card - Inches(0.8), [
        ("Zero-Hallucination Mandate:", "Guarantee that every derivation, state partition, and parse tree is 100% mathematically verified."),
        ("Full Pedagogical Explanations:", "Combine the exactness of formal compiler algorithms with the natural explanatory power of AI."),
        ("Complete Dual Export:", "Deliver publication-quality, standalone HTML dossiers and vector A4 PDF exam reports with Graphviz diagrams.")
    ])

    set_speaker_notes(
        slide2,
        "Let's begin with the core problem that motivated this project.\n\n"
        "If you ask ChatGPT or standard LLMs to minimize a 7-state DFA or generate a leftmost derivation for a context-free grammar, they sound completely convincing—but their math is frequently wrong. They skip nonterminals, confuse epsilon with a literal letter, merge accepting and non-accepting states, and report false success.\n\n"
        "Why does this happen? Because Theory of Computation requires exact, discrete state transitions, while LLMs are probabilistic next-token predictors. Our mission was to solve this fundamental flaw by decoupling mathematical computation from linguistic explanation."
    )

    # =========================================================================
    # SLIDE 3: OUR CORE PHILOSOPHY
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide3, "Core Design Paradigm", "Our Architectural Philosophy: 'Deterministic Truth, LLM Explanation'")
    add_footer(slide3, 3)

    # Two Large Column Cards
    col_w = Inches(5.66)
    col_h = Inches(5.3)
    col_y = Inches(1.45)

    add_card(slide3, Inches(0.8), col_y, col_w, col_h, "TOC Deterministic Computation Tier (The Authority)", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide3, Inches(0.8), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("Absolute Computational Authority:", "All formal mathematical derivations, state equivalence partitions, subset constructions, and graph structures are calculated exclusively by deterministic algorithms."),
        ("Cycle-Safe Earley Chart Parser:", "Employs dynamic programming to parse arbitrary context-free grammars (including left-recursive rules) in O(n^3) worst-case."),
        ("Myhill-Nerode Minimizer:", "Executes formal table-filling to identify indistinguishable states and synthesize minimal quotient DFAs."),
        ("Invariant Assertions:", "Every result is cross-checked against independent mathematical oracles (automata-lib, Moore partition refinement) before rendering.")
    ])

    add_card(slide3, Inches(6.86), col_y, col_w, col_h, "Advisory LLM Explanation Tier (The Narrator)", COLOR_NAVY)
    add_bullets_to_card(slide3, Inches(6.86), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("Strictly Constrained Sandbox:", "The LLM is fed the pre-computed 'canonical_result' dictionary and is forbidden from performing its own math."),
        ("Zero Autonomous Math:", "Prompt directive explicitly states: 'YOU MUST NOT perform your own computation. Your job is ONLY to explain the step-by-step logic matching the canonical result.'"),
        ("Structured 6-Section Narration:", "Forces Gemini to output structured markdown covering Problem Interpretation, Assumptions, Derivation Steps, Traces, Final Status, and Diagram Descriptions."),
        ("Graceful Degradation:", "If the API times out, hits rate limits, or is offline, the system bypasses the LLM and renders the verified math directly without crashing.")
    ])

    set_speaker_notes(
        slide3,
        "Here is the foundational rule of our entire architecture: 'Deterministic Truth, LLM Explanation.'\n\n"
        "We completely separate the computational engine from the narrative engine. On the left, our deterministic tier executes classical algorithms: Earley chart parsing, Myhill-Nerode minimization, and BFS reachability. It produces an immutable, mathematically verified canonical result.\n\n"
        "On the right, our advisory LLM tier takes that canonical result and translates it into a pedagogical, step-by-step explanation. The AI is strictly forbidden from recalculating the answer. If the AI hallucinates, our system rejects the proposal. If the AI goes offline, our system still renders 100% of the verified mathematical solution."
    )

    # =========================================================================
    # SLIDE 4: HIGH-LEVEL ARCHITECTURE & 6-TIER PIPELINE
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide4, "System Engineering", "High-Level System Architecture & The 6-Tier Pipeline")
    add_footer(slide4, 4)

    # 6 Tier horizontal cards (2 rows of 3)
    card_w = Inches(3.64)
    card_h = Inches(2.45)
    r1_y = Inches(1.45)
    r2_y = Inches(4.25)

    add_card(slide4, Inches(0.8), r1_y, card_w, card_h, "Tier 1: Presentation Tier (app.py)", COLOR_NAVY)
    add_bullets_to_card(slide4, Inches(0.8), r1_y + Inches(0.55), card_w, card_h - Inches(0.6), [
        ("Reactive Streamlit Engine:", "Dynamic forms, mode switcher (Mode 1 Reference vs Mode B Universal)."),
        ("Sandboxed Iframe:", "Isolates report HTML from host styling."),
        ("Session Caching:", "Persists reports across widget triggers.")
    ])

    add_card(slide4, Inches(4.84), r1_y, card_w, card_h, "Tier 2: Orchestration Tier", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide4, Inches(4.84), r1_y + Inches(0.55), card_w, card_h - Inches(0.6), [
        ("universal_generator.py:", "Normalizes inputs, dispatches tasks, and aggregates results."),
        ("Canonical Data Aggregation:", "Packages verified steps, trees, and tables into strongly typed JSON.")
    ])

    add_card(slide4, Inches(8.88), r1_y, card_w, card_h, "Tier 3: Deterministic Solvers", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide4, Inches(8.88), r1_y + Inches(0.55), card_w, card_h - Inches(0.6), [
        ("CFGSolver:", "Earley chart parser with cycle safety."),
        ("DFAMinimizer:", "Myhill-Nerode table-filling."),
        ("NFAConverter:", "Powerset subset construction with epsilon closures.")
    ])

    add_card(slide4, Inches(0.8), r2_y, card_w, card_h, "Tier 4: Mathematical Validation Gate", COLOR_EMERALD)
    add_bullets_to_card(slide4, Inches(0.8), r2_y + Inches(0.55), card_w, card_h - Inches(0.6), [
        ("validation_gate.py:", "Enforces partition purity and transition closure."),
        ("Language Equivalence:", "Uses automata-lib to assert L(DFA_orig) == L(DFA_min)."),
        ("Moore vs. Hopcroft:", "Cross-checks partition consensus.")
    ])

    add_card(slide4, Inches(4.84), r2_y, card_w, card_h, "Tier 5: Advisory AI Layer", COLOR_CYAN)
    add_bullets_to_card(slide4, Inches(4.84), r2_y + Inches(0.55), card_w, card_h - Inches(0.6), [
        ("KeyManager:", "Dynamic multi-key cycling across Gemini keys."),
        ("Advisory Commentary:", "Generates 6 structured pedagogical sections."),
        ("Deterministic Override:", "Local math always supersedes AI text.")
    ])

    add_card(slide4, Inches(8.88), r2_y, card_w, card_h, "Tier 6: Visualization & Export", COLOR_NAVY)
    add_bullets_to_card(slide4, Inches(8.88), r2_y + Inches(0.55), card_w, card_h - Inches(0.6), [
        ("Graphviz DOT:", "Automata state graphs and derivation trees."),
        ("Interactive Zoom:", "Client-side Fit, Zoom In/Out, Reset controls."),
        ("Dual Export Engine:", "Self-contained HTML + WeasyPrint vector PDF.")
    ])

    set_speaker_notes(
        slide4,
        "This slide illustrates our complete 6-tier architecture.\n\n"
        "At the top, Tier 1 is our Streamlit frontend, providing an intuitive UI with mode switching. Tier 2 is our Universal Orchestration layer, which cleans inputs and routes problems.\n\n"
        "Tier 3 contains our authoritative deterministic solvers. Crucially, before anything can be displayed, Tier 4—our Mathematical Validation Gate—checks the results against formal language theory invariants and asserts language equivalence using automata-lib.\n\n"
        "Tier 5 handles advisory AI explanations with automatic key rotation, and Tier 6 compiles interactive Graphviz diagrams with client-side zoom controls and builds our downloadable HTML and PDF reports."
    )

    # =========================================================================
    # SLIDE 5: DETERMINISTIC CFG DERIVATION ENGINE
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide5, "Deep Dive: Grammar Engineering", "Deterministic CFG Derivation & Structural Ambiguity Engine")
    add_footer(slide5, 5)

    add_card(slide5, Inches(0.8), col_y, col_w, col_h, "Quote-Aware Tokenizer & Chart Parsing", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide5, Inches(0.8), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("The Whitespace Solution:", "Splits space-separated tokens '( ( ) ) ( )' into ['(', '(', ')', ')', '(', ')'] without treating separator spaces as grammar terminals."),
        ("Quoted Multi-Character Terminals:", "Uses quote-aware regex to preserve spaces inside literals (e.g. 'a b' c -> tokens ['a b', 'c'])."),
        ("Concatenation Normalization:", "Splits rules like S -> (S)S into '(' S ')' S while protecting user-defined nonterminals (e.g., NT)."),
        ("Why Earley Chart Parsing?:", "Recursive descent crashes on left-recursive grammars like S -> S S | a. Earley parsing uses dynamic programming state sets to handle any CFG with complete cycle safety.")
    ])

    add_card(slide5, Inches(6.86), col_y, col_w, col_h, "Derivation Tracing & Ambiguity Proofs", COLOR_NAVY)
    add_bullets_to_card(slide5, Inches(6.86), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("Strict Leftmost & Rightmost Tracing:", "Traverses parse trees to expand strictly the lowest index (leftmost) or highest index (rightmost) nonterminal at each step."),
        ("Epsilon Nonterminal Elimination:", "Expanding S -> ε naturally removes the nonterminal from the frontier without emitting literal 'eps' or 'epsilon' characters."),
        ("Structural Ambiguity Discovery:", "Discovers all valid parse trees. If trees > 1, proves grammar is ambiguous and uses pre-order traversal to pinpoint the exact divergent node."),
        ("Academic Precision Disclaimer:", "If only 1 tree is found, explicitly clarifies that the grammar is unambiguous for that string, while general grammar ambiguity remains mathematically unproven.")
    ])

    set_speaker_notes(
        slide5,
        "Let's look into our CFG Derivation and Ambiguity Analysis engine.\n\n"
        "First, we solved the input tokenization problem: when students type '( ( ) ) ( )', naive parsers fail because they treat spaces as alphabet symbols. Our quote-aware tokenizer correctly cleans separator whitespace while protecting literal spaces inside quotes, like 'a b'.\n\n"
        "Second, why did we choose Earley chart parsing? Because textbooks frequently use left-recursive rules like S -> S S | a. Recursive descent parsers enter infinite recursion and crash, but Earley parsing handles any context-free grammar safely.\n\n"
        "Third, for ambiguity: when multiple trees exist, we prove ambiguity and pinpoint the exact divergence in pre-order traversal. And if only one tree exists, we provide a mathematically precise disclaimer noting that general grammar ambiguity is undecidable and unproven."
    )

    # =========================================================================
    # SLIDE 6: FINITE AUTOMATA & MINIMIZATION ENGINE
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide6, "Deep Dive: Automata Theory", "Finite Automata Engines: Minimization, Conversion & Tracing")
    add_footer(slide6, 6)

    add_card(slide6, Inches(0.8), col_y, col_w, col_h, "Myhill-Nerode Table-Filling Minimization", COLOR_NAVY)
    add_bullets_to_card(slide6, Inches(0.8), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("Step 1: Reachable State Purge:", "Executes Breadth-First Search (BFS) from start_state. Unreachable states are detected and purged before minimization, preventing corrupted equivalence classes."),
        ("Step 2: 0-Equivalence Partitioning:", "Separates reachable states into Accepting (F) and Non-Accepting (Q \\ F) groups."),
        ("Step 3: Triangular Distinguishability Matrix:", "Populates matrix M[p, q]. Iteratively marks pairs if transitions delta(p, a) and delta(q, a) lead to an already distinguished pair."),
        ("Step 4: Quotient DFA Synthesis:", "Merges unmarked indistinguishable pairs into composite states (e.g. '{q0,q1}'). Builds quotient transition tables and assigns start/final states.")
    ])

    add_card(slide6, Inches(6.86), col_y, col_w, col_h, "NFA Powerset Construction & Traces", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide6, Inches(6.86), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("Epsilon-Closure Computation:", "Uses Depth-First Search (DFS) over epsilon-transitions to compute E(q) closures."),
        ("Powerset Subset Construction:", "Constructs DFA states representing reachable subsets of NFA states. Tracks transitions across all alphabet symbols."),
        ("Explicit Trap State Handling:", "Automatically routes undefined transitions to a dedicated dead/trap state ('∅') to preserve formal DFA completeness."),
        ("Step-by-Step String Tracing:", "DFASimulator replays input strings transition-by-transition, capturing visited states and identifying acceptance or trap failure.")
    ])

    set_speaker_notes(
        slide6,
        "Turning to our Finite Automata engines, we implemented classical algorithms with zero heuristic shortcuts.\n\n"
        "For DFA minimization, many tools erroneously run table-filling over unreachable states. Our minimizer first runs BFS to purge unreachable states. Then, it sets up the 0-equivalence partition and iteratively marks the triangular distinguishability matrix until fixpoint is reached. Finally, it merges equivalent states into quotient classes like '{q0,q1}'.\n\n"
        "For NFA to DFA conversion, our converter computes epsilon-closures via DFS, builds reachable state subsets, and explicitly handles trap states so the resulting DFA is formally complete. Every step is validated against our verification layer."
    )

    # =========================================================================
    # SLIDE 7: TRI-LAYER MATHEMATICAL VERIFICATION GATE
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide7, "Mathematical Rigor", "The Tri-Layer Verification Gate: Why Our System Never Lies")
    add_footer(slide7, 7)

    # 3 Horizontal Cards (Stacked)
    h_stack = Inches(1.6)
    y1 = Inches(1.45)
    y2 = Inches(3.25)
    y3 = Inches(5.05)
    w_stack = Inches(11.733)

    add_card(slide7, Inches(0.8), y1, w_stack, h_stack, "Layer 1: Primary Deterministic Solver Execution", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide7, Inches(0.8), y1 + Inches(0.48), w_stack, h_stack - Inches(0.55), [
        ("Authoritative Computation:", "Executes custom algorithmic solvers (CFGSolver, DFAMinimizer, NFAConverter). Produces the raw candidate derivation or quotient DFA."),
        ("Syntax & Resource Verification:", "Asserts grammar production syntax, alphabet coverage, start symbol existence, and timeout bounds (5.0s, 300 tokens).")
    ])

    add_card(slide7, Inches(0.8), y2, w_stack, h_stack, "Layer 2: Formal Mathematical Validation Gate (validation_gate.py)", COLOR_EMERALD)
    add_bullets_to_card(slide7, Inches(0.8), y2 + Inches(0.48), w_stack, h_stack - Inches(0.55), [
        ("Partition Purity Check:", "Asserts that no minimized state class contains both an accepting and a non-accepting state."),
        ("automata-lib Equivalence Assertion:", "Constructs formal DFA instances and verifies L(DFA_min) == L(DFA_orig) via symmetric difference emptiness."),
        ("Dual Algorithm Cross-Check:", "Runs Moore partition refinement against Hopcroft minimizer. Halts if partition classes disagree.")
    ])

    add_card(slide7, Inches(0.8), y3, w_stack, h_stack, "Layer 3: Advisory API Verification & Discrepancy Audit", COLOR_NAVY)
    add_bullets_to_card(slide7, Inches(0.8), y3 + Inches(0.48), w_stack, h_stack - Inches(0.55), [
        ("Zero-Context Audit Query:", "Sends raw problem to Gemini in an isolated sandbox, asking for independent state counts and traces."),
        ("Discrepancy Logging:", "If the AI proposes a different number of states, logs a discrepancy warning but strictly preserves the deterministic math.")
    ])

    set_speaker_notes(
        slide7,
        "Slide 7 explains our most critical technical contribution: the Tri-Layer Verification Gate.\n\n"
        "Layer 1 is the primary deterministic solver. But we don't just trust its output. In Layer 2, our validation gate enforces three strict mathematical checks: it verifies partition purity, ensures transition closure, and uses automata-lib to prove formal language equivalence between the original and minimized machines.\n\n"
        "In Layer 3, we run an advisory audit query with Gemini. If the AI hallucinates, the discrepancy is logged, and the deterministic math strictly overrides the proposal. This tri-layer architecture guarantees that no incorrect result can ever be displayed to the user."
    )

    # =========================================================================
    # SLIDE 8: WHY WE CHOSE OUR MODELS & LIBRARIES
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide8, "Technical Decisions", "Strategic Technology Choices & Library Rationale")
    add_footer(slide8, 8)

    # Table layout of technical choices
    tb_tech = slide8.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.4))
    tf_tech = tb_tech.text_frame
    tf_tech.word_wrap = True

    tech_data = [
        ("Google Gemini Flash (3.5-flash-lite)", "Why chosen:", "Provides sub-second latency for real-time web interactivity, cost efficiency across dozens of test suites, and native JSON schema mode (response_mime_type: 'application/json') ensuring structured output."),
        ("KeyManager Rotation Pattern", "Why chosen:", "Prevents HTTP 429 quota exhaustion in educational/free-tier developer environments by cycling keys across GEMINI_API_KEYS with transparent retry and 100% offline fallback."),
        ("NLTK EarleyChartParser", "Why chosen:", "Dynamic programming algorithm handles ANY context-free grammar (including left-recursive rules like S -> S S | a) without stack overflows, while simultaneously discovering all parse trees for ambiguity analysis."),
        ("automata-lib", "Why chosen:", "Acts as an independent formal language reference oracle. Verifies that minimized DFAs and converted NFAs preserve exact language equivalence (L(M1) == L(M2))."),
        ("Graphviz DOT Engine", "Why chosen:", "Industry standard for directed graph layout. Computes optimal curved edge splines, double-circle accepting states, and balanced parse trees without overlapping text."),
        ("WeasyPrint & MathJax", "Why chosen:", "Renders LaTeX mathematical notation (⇒, ε, δ) and compiles pixel-perfect vector A4 PDF reports using CSS Paged Media standards.")
    ]

    for i, (title, prefix, body) in enumerate(tech_data):
        p = tf_tech.paragraphs[0] if i == 0 else tf_tech.add_paragraph()
        p.space_after = Pt(10)
        p.line_spacing = 1.15
        
        r_t = p.add_run()
        r_t.text = f"• {title}: "
        r_t.font.name = FONT_TITLE
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_NAVY
        
        r_b = p.add_run()
        r_b.text = body
        r_b.font.name = FONT_BODY
        r_b.font.size = Pt(10.5)
        r_b.font.color.rgb = COLOR_DARK_TEXT

    set_speaker_notes(
        slide8,
        "Here we summarize why we chose each specific tool in our stack.\n\n"
        "We picked Gemini Flash for sub-second latency and native JSON mode. We built KeyManager to eliminate API rate limits through multi-key rotation.\n\n"
        "We chose NLTK's Earley parser because it is the only parser that handles arbitrary student grammars with left recursion and extracts all parse trees. We chose automata-lib as our formal language oracle, Graphviz for topological diagramming, and WeasyPrint for publication-quality PDF generation."
    )

    # =========================================================================
    # SLIDE 9: END-TO-END WORKFLOW & USER EXPERIENCE
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide9, "User Experience & Workflow", "End-to-End Workflow & Interactive User Experience")
    add_footer(slide9, 9)

    add_card(slide9, Inches(0.8), col_y, col_w, col_h, "The Execution Pipeline", COLOR_NAVY)
    add_bullets_to_card(slide9, Inches(0.8), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("1. Intuitive Parameter Ingestion:", "User inputs Grammar, Alphabet, Start Symbol, Target String, and Derivation Mode in Streamlit."),
        ("2. Real-Time Deterministic Solving:", "CFGSolver/DFAMinimizer executes within 50ms, producing validated derivation tables and state matrices."),
        ("3. Validation & Advisory AI Pass:", "ValidationGate verifies invariants; Gemini Flash generates structured pedagogical narration."),
        ("4. Seamless Iframe Presentation:", "Renders responsive HTML inside st.components.v1.html with MathJax typography and Unicode derivation sequences.")
    ])

    add_card(slide9, Inches(6.86), col_y, col_w, col_h, "Interactive Inspection & Dual Export", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide9, Inches(6.86), col_y + Inches(0.65), col_w, col_h - Inches(0.8), [
        ("Client-Side Interactive Zoom Controls:", "Every diagram figure is equipped with 'Fit', 'Zoom In (+)', 'Zoom Out (-)', and 'Reset' buttons. Scales dynamically in DOM via 'data-scale' attribute without server reloads."),
        ("Responsive Layout & Color Contrast:", "Table containers support horizontal scrolling; CSS custom properties ensure WCAG AA compliant contrast in light and dark modes."),
        ("Standalone HTML Export:", "Bundles all CSS, MathJax formulas, and base64-encoded SVG/PNG diagrams into a self-contained, portable file."),
        ("Academic PDF Export:", "Compiles vector-sharp A4 PDF documents ready for academic grading and submission.")
    ])

    set_speaker_notes(
        slide9,
        "Slide 9 demonstrates the user experience and export capabilities.\n\n"
        "From the user's perspective, they input their grammar or automaton, click Generate, and receive an instant, beautiful report. The derivation table, mathematical sequence, and parse trees are rendered with high-contrast typography.\n\n"
        "Crucially, we implemented client-side zoom controls: users can zoom in, zoom out, fit, and reset large parse trees directly in the browser with zero lag. And when they're done, they can download a standalone HTML report with embedded base64 images, or an exam-ready PDF."
    )

    # =========================================================================
    # SLIDE 10: VERIFICATION RESULTS & CONCLUSION
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header_banner(slide10, "Impact & Conclusion", "Verification Results, Impact & Project Deliverables")
    add_footer(slide10, 10)

    # Top highlight card
    add_card(slide10, Inches(0.8), Inches(1.45), Inches(11.733), Inches(1.7), "Automated Testing & Quality Assurance", COLOR_EMERALD, bg_color=RGBColor(236, 253, 245), border_color=RGBColor(16, 185, 129))
    add_bullets_to_card(slide10, Inches(0.8), Inches(1.95), Inches(11.733), Inches(1.1), [
        ("100% Test Pass Rate:", "26 automated unit and regression tests pass across 5 specialized test suites (CFG correctness, tokenization, rendering, DFA minimization, export pipeline)."),
        ("Headless Browser UI Verification:", "Automated Playwright tests verify live DOM rendering, zoom button scaling, table scrolling, and theme contrast on the running Streamlit server.")
    ])

    # Bottom Two Cards
    b_y = Inches(3.35)
    b_h = Inches(3.4)

    add_card(slide10, Inches(0.8), b_y, col_w, b_h, "Project Deliverables & Artifacts", COLOR_NAVY)
    add_bullets_to_card(slide10, Inches(0.8), b_y + Inches(0.65), col_w, b_h - Inches(0.8), [
        ("GitHub Repository:", "https://github.com/AryanSharma221/toc-answer-generator"),
        ("Technical Architecture Manual:", "TOC_System_Architecture_and_Workflow.docx"),
        ("Teammate Deep-Dive Guide:", "TOC_Project_Deep_Dive_and_Design_Decisions.docx"),
        ("Presentation Deck:", "TOC_Presentation_Slides.pptx (16:9 Widescreen)"),
        ("Live Web Application:", "Interactive Streamlit platform on port 8501/8502.")
    ])

    add_card(slide10, Inches(6.86), b_y, col_w, b_h, "Final Key Takeaway", COLOR_SLATE_BLUE)
    add_bullets_to_card(slide10, Inches(6.86), b_y + Inches(0.65), col_w, b_h - Inches(0.8), [
        ("A Blueprint for AI in STEM:", "Proves that AI in technical education should never be a black-box oracle. By constraining LLMs to explain verified deterministic algorithms, we achieve zero hallucinations with maximum pedagogical value."),
        ("Extensible Architecture:", "The modular solver-orchestrator pattern easily scales to Turing Machines, Pushdown Automata, and LL/LR parser generators."),
        ("Thank You! Questions & Discussion:", "We are ready for questions and a live demo!")
    ])

    set_speaker_notes(
        slide10,
        "To conclude, our Theory of Computation Answer Generator achieves a 100% test pass rate across 26 unit tests and end-to-end Playwright browser tests.\n\n"
        "We have published the entire open-source repository on GitHub, along with comprehensive Word documentation and this slide deck.\n\n"
        "Our project demonstrates a vital principle for the future of AI in technical education: AI should never be trusted as a black-box calculator for formal math. By pairing authoritative compiler algorithms with advisory AI explanation, we get the best of both worlds: mathematical perfection and clear, natural communication. Thank you, and we welcome your questions!"
    )

    target_path = os.path.abspath("TOC_Presentation_Slides.pptx")
    prs.save(target_path)
    print(f"Presentation deck successfully created and saved at: {target_path}")
    return target_path

if __name__ == "__main__":
    build_all_slides()
