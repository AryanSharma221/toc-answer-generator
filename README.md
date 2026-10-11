# Theory of Computation Answer Generator & Formal Languages Workbench

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Author](https://img.shields.io/badge/Author-Aryan%20Sharma-blueviolet.svg)](https://github.com/AryanSharma221)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive, rigorous Theory of Computation (TOC) problem solver, visualizer, and examination report generator built with **Python**, **Streamlit**, **NLTK**, and **Graphviz**.

Developed by **Aryan Sharma** ([@AryanSharma221](https://github.com/AryanSharma221)).

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
  - [Mode A: Reference Examination Solver](#mode-a-reference-examination-solver)
  - [Mode B: Universal Specification Engine](#mode-b-universal-specification-engine)
    - [1. CFG Derivation & Ambiguity Analysis](#1-cfg-derivation--ambiguity-analysis)
    - [2. DFA Minimization](#2-dfa-minimization)
    - [3. NFA to DFA Subset Construction](#3-nfa-to-dfa-subset-construction)
    - [4. Regular Expressions to DFA](#4-regular-expressions-to-dfa)
- [Interactive Visualizations & Zoom Controls](#interactive-visualizations--zoom-controls)
- [Project Architecture](#project-architecture)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
  - [Running the Web Interface](#running-the-web-interface)
  - [CFG Input Formatting Rules](#cfg-input-formatting-rules)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Exporting Reports](#exporting-reports)
- [Author](#author)
- [License](#license)

---

## Overview

The **Theory of Computation Answer Generator** bridges the gap between abstract formal language theory and concrete, step-by-step mathematical solutions. It combines deterministic formal algorithms (Earley chart parsing, Myhill-Nerode table filling, powerset construction) with automated diagram generation and an academic-grade report exporter.

Whether analyzing complex context-free grammars for ambiguity, deriving strings leftmost or rightmost, converting non-deterministic automata to deterministic ones, or minimizing DFAs, this workbench generates complete mathematical steps, state transition tables, visual trees/graphs, and verified final yields.

---

## Key Features

### Mode A: Reference Examination Solver
Provides verified, exhaustive solutions for standard curricular reference problems:
- **Question 1: Time-Machine Paradox Checker**:
  - Deterministic Finite Automaton (DFA) state design and formal 5-tuple specification.
  - Table-filling state equivalence minimization.
  - Formal Pumping Lemma non-regularity proof with adversary game steps.
- **Question 2: Treasure Hunter's Cave Diary**:
  - Context-Free Grammar (CFG) formal 4-tuple specification.
  - Leftmost and rightmost derivations.
  - Parse tree generation and structural ambiguity analysis.
  - Pumping Lemma for Context-Free Languages (CFLs).

---

### Mode B: Universal Specification Engine
A deterministic solver that accepts arbitrary formal specifications and solves problems on demand:

#### 1. CFG Derivation & Ambiguity Analysis
- **Leftmost & Rightmost Derivations**: Derives any target string step-by-step, strictly expanding only the leftmost or rightmost non-terminal at each step.
- **Earley Chart Parsing (`nltk`)**: Robust chart parsing that prevents infinite recursion loops on arbitrary left-recursive or right-recursive grammars.
- **Ambiguity Detection**:
  - Discovers all distinct parse trees for a given string.
  - If $>1$ distinct trees exist, reports the grammar as **Ambiguous** and provides an automated pre-order structural divergence analysis.
  - If only 1 tree is found, displays an explicit mathematical disclaimer that ambiguity for this specific string is resolved while general grammar ambiguity remains unproven.
- **Flexible Tokenizer**:
  - Space-separated token format (e.g. `( ( ) ) ( )` $\rightarrow$ `["(", "(", ")", ")", "(", ")"]` with yield `(())()`).
  - Preserves whitespace inside quoted multi-character terminals (e.g. `'a b' c` $\rightarrow$ `["a b", "c"]`).
  - Strict empty string (`ε`, `eps`, `epsilon`) handling.
- **Resource Guardrails**: Built-in limits (`max_tokens=300`, `timeout=5.0s`, `max_trees=100`) returning `Search Incomplete` rather than false impossibility or false success.

#### 2. DFA Minimization
- Implements the **Table-Filling Algorithm** based on the Myhill-Nerode theorem.
- Automatically detects and removes unreachable states from the start state.
- Generates 0-equivalent and 1-equivalent partition tables, merged equivalence classes, and the minimized DFA transition table.

#### 3. NFA to DFA Subset Construction
- Powerset / subset construction algorithm with $\epsilon$-closure computation.
- Traverses reachable state subsets, detects trap/dead states, and identifies final states.
- Generates subset mapping tables, converted DFA transition tables, and language verification checks.

#### 4. Regular Expressions to DFA
- Parses regular expressions and converts them into equivalent minimal DFAs using Thompson's construction and subset determinization.

---

## Interactive Visualizations & Zoom Controls

Every generated diagram is embedded with client-side interactive inspection controls:
- **Fit**: Fits the diagram within the view container.
- **Zoom In (+)**: Dynamically scales up the SVG/PNG diagram by 25% increments for inspecting deeply nested trees.
- **Zoom Out (-)**: Scales down the diagram.
- **Reset**: Instantly restores default scaling and alignment.
- **High-Contrast Responsive Styling**: Seamlessly supports both light and dark modes with WCAG AA compliant contrast ratios.

---

## Project Architecture

```
toc_answer_generator/
├── app.py                                # Streamlit main application entry point
├── requirements.txt                      # Project dependencies
├── core/
│   ├── universal_generator.py            # Universal engine & typed HTML report generator
│   ├── independent_verifier.py          # Verification layer & data validation
│   ├── validation_gate.py               # Deterministic mathematical validation gate
│   ├── question_specific_generator_q1.py# Question 1 reference solver
│   └── question_specific_generator_q2.py# Question 2 reference solver
├── solvers/
│   ├── cfg_solver.py                     # CFG parsing, derivation, & ambiguity engine
│   └── dfa_minimizer.py                 # Myhill-Nerode DFA minimization solver
├── diagrams/
│   ├── cfg_tree_renderer.py              # Graphviz parse-tree rendering
│   └── dfa_renderer.py                  # Graphviz finite-state diagram rendering
├── exporters/
│   ├── html_exporter.py                  # HTML report bundler with base64 embedded assets
│   └── pdf_exporter.py                   # WeasyPrint PDF export engine
├── tests/
│   ├── test_cfg_comprehensive_regression.py # Comprehensive 7-test backend regression suite
│   ├── test_browser_regression_full.py       # Playwright end-to-end browser test suite
│   ├── test_cfg_ambiguity_tokenization.py   # Tokenization & ambiguity unit tests
│   ├── test_cfg_rendering_regression.py     # HTML & MathJax rendering regression tests
│   └── ...                                  # Automata & conversion unit tests
└── data/                                 # Question paper definitions & references
```

---

## Installation & Setup

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12.
- **Graphviz**: Required for rendering state machine and parse tree diagrams.

#### Install Graphviz:
- **Windows (PowerShell)**:
  ```powershell
  winget install graphviz --accept-source-agreements --accept-package-agreements
  ```
  *Ensure `C:\Program Files\Graphviz\bin` is added to your system `PATH`.*
- **macOS**:
  ```bash
  brew install graphviz
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get update && sudo apt-get install -y graphviz
  ```

### 2. Clone the Repository
```bash
git clone https://github.com/AryanSharma221/toc-answer-generator.git
cd toc-answer-generator
```

### 3. Create Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Usage Guide

### Running the Web Interface
Launch the Streamlit web application:
```powershell
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501` (or the port displayed in your terminal).

### CFG Input Formatting Rules
In **Mode B: CFG Solver**, configure your grammar and inputs:
- **Grammar Editor**: One production per line or separated by `|`:
  ```text
  S -> ( S ) S | epsilon
  ```
  or:
  ```text
  S -> S S | a
  ```
- **Start Symbol**: e.g., `S`.
- **Alphabet**: Comma-separated terminals, e.g., `(, )` or `a, b`.
- **Target String**: Enter tokens space-separated (e.g. `( ( ) ) ( )` or `a a a`).
- **Derivation Selection**: Choose between **Leftmost** or **Rightmost** derivation.
- Click **Generate CFG Solution** to inspect derivations, tables, and parse trees.

---

## Testing & Quality Assurance

The project includes an extensive suite of automated unit, integration, and browser end-to-end tests:

### 1. Run Complete CFG Regression Suite
```powershell
$env:PYTHONPATH=(Get-Location)
python -m unittest tests/test_cfg_comprehensive_regression.py
```
Verifies:
- **Test 1**: Nested parentheses (`S -> ( S ) S | epsilon`, target `(())()`).
- **Test 2**: Simple recursion (`S -> a S b | epsilon`, target `aabb`).
- **Test 3**: Empty string derivations (`S -> a S | epsilon`, target `""`).
- **Test 4**: Deterministic rejection of invalid strings (`S -> a S | epsilon`, target `ab`).
- **Test 5**: Ambiguous grammar detection and dual parse trees (`S -> S S | a`, target `aaa`).
- **Test 6**: Rightmost derivation nonterminal expansion invariants (`S -> A B`, target `aabb`).
- **Test 7**: Whitespace and quote tokenization robustness.

### 2. Run Interactive Playwright Browser UI Tests
```powershell
$env:PYTHONPATH=(Get-Location); $env:PYTHONIOENCODING="utf-8"
python tests/test_browser_regression_full.py
```
Validates real browser rendering, dynamic zoom button scaling (`Fit`, `Zoom In`, `Zoom Out`, `Reset`), responsive overflow, and color contrast.

---

## Exporting Reports
From the Streamlit web interface:
- **Download HTML Report**: Exports a standalone, portable HTML file with all CSS, MathJax formulas, and base64-encoded SVG/PNG diagrams embedded.
- **Download PDF Report**: Generates an exam-ready, formatted PDF document via WeasyPrint.

---

## Author

**Aryan Sharma**
- GitHub: [@AryanSharma221](https://github.com/AryanSharma221)
- Email: [dedinside69696956@gmail.com](mailto:dedinside69696956@gmail.com)

---

## License

This project is open-source and licensed under the [MIT License](LICENSE).
