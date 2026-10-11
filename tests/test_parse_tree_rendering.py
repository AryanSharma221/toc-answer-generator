import os
from core.question_specific_generator_q2 import generate_q2
from core.universal_generator import solve_universal

def test_parse_tree_rendering():
    generate_q2()
    
    solve_universal("CFG Derivation", {
        "grammar": "S -> aSb | epsilon",
        "start_symbol": "S",
        "input_tokens": list("aaabbb")
    })
    
    solve_universal("CFG Derivation", {
        "grammar": "E -> E '+' E | E '*' E | 'id'",
        "start_symbol": "E",
        "input_tokens": ["id", "+", "id", "*", "id"]
    })
    
    print("Parse trees generated.")

if __name__ == "__main__":
    test_parse_tree_rendering()
