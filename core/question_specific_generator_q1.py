import uuid
import os
import sys

# To support importing our core modules when run directly or imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diagrams.dfa_renderer import render_dfa_diagram

def render_dfa(states, alphabet, transitions, start_state, accepting_states, filename='dfa'):
    return render_dfa_diagram({
        'states': states,
        'alphabet': alphabet,
        'transitions': transitions,
        'start_state': start_state,
        'accepting_states': accepting_states
    }, filename=filename)
from diagrams.parse_tree_renderer import render_parse_tree

def generate_q1(selected_subquestions=None):
    print("Generating Q1...")
    
    if selected_subquestions is None:
        selected_subquestions = ['a', 'b', 'c', 'd']
        
    dfa_path = ""
    if 'a' in selected_subquestions:
        # Q1(a) DFA
        states = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        alphabet = ['p', 'f', 'h']
        transitions = {
            'A': {'p': 'F', 'f': 'A', 'h': 'B'},
            'B': {'p': 'F', 'f': 'A', 'h': 'B'},
            'C': {'p': 'F', 'f': 'G', 'h': 'B'},
            'D': {'p': 'C', 'f': 'D', 'h': 'E'},
            'E': {'p': 'C', 'f': 'D', 'h': 'E'},
            'F': {'p': 'C', 'f': 'G', 'h': 'E'},
            'G': {'p': 'G', 'f': 'G', 'h': 'G'},
        }
        dfa_path = render_dfa(states, alphabet, transitions, 'A', ['B'], filename=f'q1a_dfa_reconstructed_{uuid.uuid4().hex[:8]}')

    dfa_min_path = ""
    if 'b' in selected_subquestions:
        # Q1(b) Minimized DFA
        states_min = ['A', 'B', 'C', '{D,E}', 'F', 'G']
        transitions_min = {
            'A': {'p': 'F', 'f': 'A', 'h': 'B'},
            'B': {'p': 'F', 'f': 'A', 'h': 'B'},
            'C': {'p': 'F', 'f': 'G', 'h': 'B'},
            '{D,E}': {'p': 'C', 'f': '{D,E}', 'h': '{D,E}'},
            'F': {'p': 'C', 'f': 'G', 'h': '{D,E}'},
            'G': {'p': 'G', 'f': 'G', 'h': 'G'},
        }
        dfa_min_path = render_dfa(states_min, alphabet, transitions_min, 'A', ['B'], filename=f'q1b_dfa_min_reconstructed_{uuid.uuid4().hex[:8]}')

    all_subquestions = [
            {
                "id": "a",
                "question": "(a)  Construct a DFA for paradox-free logs. Label every state with what it remembers, and include the dead state.  [4 marks]",
                "answer": (
                    "<p>To check the three rules, the DFA tracks three things: the parity of p's, whether the last symbol was p (to catch \"pf\"), and whether the last symbol was h (for the \"must end with h\" rule).</p>\n"
                    "<table border='1'><tr><th>State</th><th>Meaning</th><th>on p</th><th>on f</th><th>on h</th></tr>"
                    "<tr><td>&rarr; A</td><td>even #p, last symbol is neither p nor h (start, or just read f)</td><td>F</td><td>A</td><td>B</td></tr>"
                    "<tr><td>B (accepting)</td><td>even #p, last symbol is h</td><td>F</td><td>A</td><td>B</td></tr>"
                    "<tr><td>C</td><td>even #p, last symbol is p</td><td>F</td><td>G</td><td>B</td></tr>"
                    "<tr><td>D</td><td>odd #p, last symbol is f</td><td>C</td><td>D</td><td>E</td></tr>"
                    "<tr><td>E</td><td>odd #p, last symbol is h</td><td>C</td><td>D</td><td>E</td></tr>"
                    "<tr><td>F</td><td>odd #p, last symbol is p</td><td>C</td><td>G</td><td>E</td></tr>"
                    "<tr><td>G</td><td>dead (a \"pf\" has occurred)</td><td>G</td><td>G</td><td>G</td></tr></table>\n"
                    "<p>Only B is accepting. Reading p flips the parity and moves to a \"last was p\" state. Reading f right after p goes to the dead state G.</p>\n"
                    f"<figure><img src=\"{dfa_path}\" /><figcaption>Figure 1. DFA for paradox-free logs (7 states, B accepting, G dead)</figcaption></figure>\n"
                    "<p>Trace of \"phfph\": A &rarr;p F &rarr;h E &rarr;f D &rarr;p C &rarr;h B. This is accepted &check;.</p>\n"
                    "<p>Trace of \"ppfh\": A &rarr;p F &rarr;p C &rarr;f G &rarr;h G. This is rejected &check;.</p>"
                )
            },
            {
                "id": "b",
                "question": "(b)  Minimize your DFA using the table-filling method. How many states does the minimal DFA have?  [2 marks]",
                "answer": (
                    "<p>Round 0: B is accepting and everything else is not, so mark (B, every other state).</p>\n"
                    "<p>Round 1: on h, the pairs (A,D), (A,E), (A,F), (A,G), (C,D), (C,E), (C,F) and (C,G) all lead to (B, non-B), which is already marked, so mark them.</p>\n"
                    "<p>Round 2: (A,C) is marked, because on f it goes to (A,G). (D,G), (E,G) and (F,G) are marked, because on p they go to (C,G).</p>\n"
                    "<p>Round 3: (D,F) and (E,F) are marked, because on f they go to (D,G) and (E,G).</p>\n"
                    "<p>Left unmarked: only (D, E). They have identical transitions and are both non-accepting, so D &equiv; E.</p>\n"
                    "<p>The minimal DFA has 6 states: A, B, C, F, {D,E}, G.</p>\n"
                    "<table border='1'><tr><th>State</th><th>on p</th><th>on f</th><th>on h</th></tr>"
                    "<tr><td>&rarr; A</td><td>F</td><td>A</td><td>B</td></tr>"
                    "<tr><td>B (accepting)</td><td>F</td><td>A</td><td>B</td></tr>"
                    "<tr><td>C</td><td>F</td><td>G</td><td>B</td></tr>"
                    "<tr><td>{D,E}</td><td>C</td><td>{D,E}</td><td>{D,E}</td></tr>"
                    "<tr><td>F</td><td>C</td><td>G</td><td>{D,E}</td></tr>"
                    "<tr><td>G</td><td>G</td><td>G</td><td>G</td></tr></table>\n"
                    f"<figure><img src=\"{dfa_min_path}\" /><figcaption>Figure 2. Minimal DFA (6 states) after merging D and E</figcaption></figure>"
                )
            },
            {
                "id": "c",
                "question": "(c)  The regulator adds a stricter rule: every past-jump must be repaid by exactly one future-jump, with all past-jumps first, then all future-jumps, then a final hold. This gives L_rep = { p&#x207f; f&#x207f; h | n &ge; 1 }. Prove L_rep is not regular using the Pumping Lemma.  [4 marks]",
                "answer": (
                    "<p>Assume L_rep is regular with pumping length m. Take w = p&#x1D5A; f&#x1D5A; h, so |w| &ge; m. Split w = xyz with |xy| &le; m and |y| &ge; 1.</p>\n"
                    "<p>Since |xy| &le; m, both x and y lie inside the p-block, so y = p&#x1D4F; with 1 &le; k &le; m. Pump with i = 2:</p>\n"
                    "<p>xy&sup2;z = p&#x1D5A;&#x207A;&#x1D4F; f&#x1D5A; h</p>\n"
                    "<p>This has more p's than f's, so it is not in L_rep. That contradicts the Pumping Lemma, so L_rep is not regular &blacksquare;</p>"
                )
            },
            {
                "id": "d",
                "question": "(d)  A colleague claims L_bal = { w &isin; {p,f,h}* | #p(w) = #f(w) } is regular. Refute this using closure under intersection with p*f*.  [2 marks]",
                "answer": (
                    "<p>Intersect L_bal with the regular language p*f*:</p>\n"
                    "<p>L_bal &cap; p*f* = { p&#x207f;f&#x207f; | n &ge; 0 }</p>\n"
                    "<p>This language is not regular, by the same pumping argument as in (c). Regular languages are closed under intersection, and p*f* is regular. If L_bal were regular, the intersection would be regular too, which is a contradiction. So L_bal is not regular &blacksquare;</p>"
                )
            }
        ]
    
    preamble = (
        "<p>A time machine logs every action over &Sigma; = {p, f, h}:</p>\n"
        "<ul>\n"
        "<li>p: jump into the past</li>\n"
        "<li>f: jump into the future</li>\n"
        "<li>h: hold position</li>\n"
        "</ul>\n"
        "<p>A trip log is paradox-free if all three rules hold:</p>\n"
        "<ul>\n"
        "<li>A jump into the past is never immediately followed by a jump into the future. There is no \"pf\" substring.</li>\n"
        "<li>The number of past-jumps is even. Otherwise a copy of the traveller is stranded in the past.</li>\n"
        "<li>The log ends with h, because the machine must be stationary to land.</li>\n"
        "</ul>\n"
        "<p>Valid: \"h\", \"fh\", \"pph\", \"phph\", \"phfph\"</p>\n"
        "<p>Invalid: \"\", \"ph\", \"ppfh\", \"pphf\", \"pphp\"</p>"
    )

    content = {
        "title": "1. Finite Automata: Time-Machine Paradox Checker (12 marks)",
        "preamble": preamble,
        "subquestions": [sq for sq in all_subquestions if sq["id"] in selected_subquestions]
    }
    return content
