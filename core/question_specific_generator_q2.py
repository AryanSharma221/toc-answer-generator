import uuid
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diagrams.parse_tree_renderer import render_parse_tree

def generate_q2(selected_subquestions=None):
    print("Generating Q2...")
    
    if selected_subquestions is None:
        selected_subquestions = ['a', 'b', 'c', 'd']
        
    path_q2b = ""
    if 'b' in selected_subquestions:
        # Q2(b) Parse Tree
        tree_q2b = {
            'id': '0', 'label': 'D', 'children': [
            {'id': '1', 'label': 'C', 'children': [
                {'id': '2', 'label': 'e'},
                {'id': '3', 'label': 'A', 'children': [
                    {'id': '4', 'label': 'm'},
                    {'id': '5', 'label': 'A', 'children': [
                        {'id': '6', 'label': 'C', 'children': [
                            {'id': '7', 'label': 'e'},
                            {'id': '8', 'label': 'A', 'children': [{'id': '9', 'label': '\u03b5'}]},
                            {'id': '10', 'label': 't'},
                            {'id': '11', 'label': 'B', 'children': [{'id': '12', 'label': '\u03b5'}]},
                            {'id': '13', 'label': 'x'}
                        ]},
                        {'id': '14', 'label': 'A', 'children': [{'id': '15', 'label': '\u03b5'}]}
                    ]}
                ]},
                {'id': '16', 'label': 't'},
                {'id': '17', 'label': 'B', 'children': [
                    {'id': '18', 'label': '\u03b5'}
                ]},
                {'id': '19', 'label': 'x'}
            ]}
        ]
        }
        path_q2b = render_parse_tree(tree_q2b, filename=f'q2b_parse_tree_reconstructed_{uuid.uuid4().hex[:8]}')

    path_q2c_1 = ""
    path_q2c_2 = ""
    if 'c' in selected_subquestions:
        # Q2(c) Ambiguity Tree 1
        tree_q2c_1 = {
            'id': '0', 'label': 'D', 'children': [
                {'id': '1', 'label': 'C', 'children': [
                    {'id': '2', 'label': 'e'},
                    {'id': '3', 'label': 'X', 'children': [{'id': '4', 'label': '\u03b5'}]},
                    {'id': '5', 'label': 't'},
                    {'id': '6', 'label': 'X', 'children': [
                        {'id': '7', 'label': 't'},
                        {'id': '8', 'label': 'X', 'children': [{'id': '9', 'label': '\u03b5'}]}
                    ]},
                    {'id': '10', 'label': 'x'}
                ]}
            ]
        }
        path_q2c_1 = render_parse_tree(tree_q2c_1, filename=f'q2c_parse_tree_1_reconstructed_{uuid.uuid4().hex[:8]}')

        # Q2(c) Ambiguity Tree 2
        tree_q2c_2 = {
            'id': '0', 'label': 'D', 'children': [
                {'id': '1', 'label': 'C', 'children': [
                    {'id': '2', 'label': 'e'},
                    {'id': '3', 'label': 'X', 'children': [
                        {'id': '4', 'label': 't'},
                        {'id': '5', 'label': 'X', 'children': [{'id': '6', 'label': '\u03b5'}]}
                    ]},
                    {'id': '7', 'label': 't'},
                    {'id': '8', 'label': 'X', 'children': [{'id': '9', 'label': '\u03b5'}]},
                    {'id': '10', 'label': 'x'}
                ]}
            ]
        }
        path_q2c_2 = render_parse_tree(tree_q2c_2, filename=f'q2c_parse_tree_2_reconstructed_{uuid.uuid4().hex[:8]}')

    all_subquestions = [
            {
                "id": "a",
                "question": "(a)  Construct a CFG for valid diaries. Explain the role of each non-terminal.  [5 marks]",
                "answer": (
                    "<p>D &rarr; C D | C<br>C &rarr; e A t B x<br>A &rarr; m A | C A | &epsilon;<br>B &rarr; t B | m B | C B | &epsilon;</p>\n"
                    "<table border='1'><tr><th>Non-terminal</th><th>Role</th></tr>"
                    "<tr><td>D</td><td>the whole diary, one or more complete caves in sequence</td></tr>"
                    "<tr><td>C</td><td>one cave: e, then contents, then x</td></tr>"
                    "<tr><td>A</td><td>the stuff before the cave's first direct treasure: monsters and whole nested caves, but no direct t</td></tr>"
                    "<tr><td>B</td><td>anything after that first direct treasure: t, m or whole caves</td></tr></table>\n"
                    "<p>The \"A t B\" shape forces every cave to have a direct treasure. The nested caves inside A and B are whole C's, so their treasures are never counted for the outer cave. This grammar is also unambiguous, as part (c) shows.</p>"
                )
            },
            {
                "id": "b",
                "question": "(b)  Give a leftmost derivation and a parse tree for \"emetxtx\".  [2 marks]",
                "answer": (
                    "<p>Leftmost derivation</p>\n"
                    "<pre>\nD &rArr; C                          (D &rarr; C)\n"
                    "  &rArr; e A t B x                  (C &rarr; e A t B x)\n"
                    "  &rArr; e m A t B x                (A &rarr; m A)\n"
                    "  &rArr; e m C A t B x              (A &rarr; C A)\n"
                    "  &rArr; e m e A t B x A t B x      (C &rarr; e A t B x)\n"
                    "  &rArr; e m e t B x A t B x        (A &rarr; &epsilon;)\n"
                    "  &rArr; e m e t x A t B x          (B &rarr; &epsilon;)\n"
                    "  &rArr; e m e t x t B x            (A &rarr; &epsilon;)\n"
                    "  &rArr; e m e t x t x              (B &rarr; &epsilon;)\n</pre>"
                    "<p>Parse tree</p>\n"
                    f"<figure><img src=\"{path_q2b}\" /><figcaption>Figure 3. Parse tree for \"emetxtx\" (yield: e m e t x t x)</figcaption></figure>"
                )
            },
            {
                "id": "c",
                "question": "(c)  A junior writes this grammar:  [3 marks]\n\nD &rarr; C D | C\nC &rarr; e X t X x\nX &rarr; C X | t X | m X | &epsilon;\n\nShow that it is ambiguous by drawing two parse trees for \"ettx\". Then give an unambiguous grammar for the same language.",
                "answer": (
                    "<p>For \"ettx\", the grammar can't tell which t is \"the required treasure\".</p>\n"
                    "<p>Leftmost derivation 1 (first t is the required one):<br>D &rArr; C &rArr; e X t X x &rArr; e t X x &rArr; e t t X x &rArr; e t t x</p>\n"
                    "<p>Leftmost derivation 2 (second t is the required one):<br>D &rArr; C &rArr; e X t X x &rArr; e t X t X x &rArr; e t t X x &rArr; e t t x</p>\n"
                    "<p>The two derivations use different rules, so they give two different parse trees for the same string, and the grammar is ambiguous &blacksquare;</p>\n"
                    f"<figure><img src=\"{path_q2c_1}\" /><figcaption>Parse tree 1 for \"ettx\"</figcaption></figure>\n"
                    f"<figure><img src=\"{path_q2c_2}\" /><figcaption>Parse tree 2 for \"ettx\"</figcaption></figure>\n"
                    "<p>Unambiguous replacement: the grammar from (a). In \"e A t B x\", A can never produce a direct t, so the t in the middle is always the first direct treasure. A and B each split the contents into items (m, t or a whole cave) in only one way. So every valid diary has exactly one parse tree.</p>"
                )
            },
            {
                "id": "d",
                "question": "(d)  Let L be the language of valid diaries. Prove L is not regular by intersecting it with e*(tx)* and applying the Pumping Lemma to the result.  [2 marks]",
                "answer": (
                    "<p>Intersect L with the regular language e*(tx)*.</p>\n"
                    "<p>A string e&#x1D5A; (tx)&#x1D47; is balanced only when a = b, and a &ge; 1 is needed because the empty diary is invalid.</p>\n"
                    "<p>Every such string is valid. In e&#x207f;(tx)&#x207f;, the innermost cave contains a t, and each outer cave gets its own t right after the inner cave closes. For example, n = 2 gives \"eetxtx\".</p>\n"
                    "<p>So L &cap; e*(tx)* = { e&#x207f;(tx)&#x207f; | n &ge; 1 }.</p>\n"
                    "<p>Assume this is regular with pumping length m, and take w = e&#x1D5A;(tx)&#x1D5A;. Since |xy| &le; m, y = e&#x1D4F; with k &ge; 1. Pumping gives e&#x1D5A;&#x207A;&#x1D4F;(tx)&#x1D5A;, which has more e's than x's, so it is not in the language. That is a contradiction.</p>\n"
                    "<p>Regular languages are closed under intersection with regular languages. If L were regular, the intersection would be regular. So L is not regular &blacksquare;</p>"
                )
            }
        ]
    
    preamble = (
        "<p>An explorer's diary is written over &Sigma; = {e, x, t, m}:</p>\n"
        "<ul>\n"
        "<li>e: enter a cave</li>\n"
        "<li>x: exit the cave you are currently in</li>\n"
        "<li>t: find a treasure</li>\n"
        "<li>m: meet a monster</li>\n"
        "</ul>\n"
        "<p>A diary is valid if all three rules hold:</p>\n"
        "<ul>\n"
        "<li>It consists of one or more complete caves in sequence. Every cave entered is exited, and you cannot exit a cave you haven't entered.</li>\n"
        "<li>Treasures and monsters occur only inside a cave.</li>\n"
        "<li>Every cave contains at least one treasure found directly in it. A treasure found only inside a nested cave does not count for the outer cave.</li>\n"
        "</ul>\n"
        "<p>Valid: \"etx\", \"emtx\", \"etmtx\", \"etxetx\", \"eetxtx\", \"emetxtx\"</p>\n"
        "<p>Invalid: \"\", \"ex\", \"emx\", \"eetxx\", \"tx\", \"etxx\", \"etxm\"</p>"
    )

    content = {
        "title": "2. Context-Free Grammar: Treasure Hunter's Cave Diary (12 marks)",
        "preamble": preamble,
        "subquestions": [sq for sq in all_subquestions if sq["id"] in selected_subquestions]
    }
    return content

if __name__ == '__main__':
    from core.question_specific_generator_q1 import generate_q1
    print(generate_q1())
    print(generate_q2())

