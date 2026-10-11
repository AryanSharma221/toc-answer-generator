import json
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html

def run_test_cases():
    # Test case 1
    # Alphabet: {0,1}
    # Language: Strings containing an even number of 0s and ending in 1.
    tc1_data = {
        "states": ["Q0", "Q1", "Q2", "Q3"],
        "alphabet": ["0", "1"],
        "start_state": "Q0",
        "accepting_states": ["Q1"],
        "state_meanings": {
            "Q0": "Even 0s, ends in non-1 or start",
            "Q1": "Even 0s, ends in 1",
            "Q2": "Odd 0s, ends in non-1",
            "Q3": "Odd 0s, ends in 1"
        },
        "transitions": {
            "Q0": {"0": "Q2", "1": "Q1"},
            "Q1": {"0": "Q2", "1": "Q1"},
            "Q2": {"0": "Q0", "1": "Q3"},
            "Q3": {"0": "Q0", "1": "Q3"}
        },
        "strings": ["1", "01", "001", "0001", ""]
    }
    
    tc1_result = solve_universal("String Acceptance Traces", tc1_data)
    print("Test Case 1 Result generated.")
    
    # Check trace outputs
    html = tc1_result['subquestions'][0]['answer']
    assert "<strong>1</strong>: Q0 --1--> Q1 => <strong>Accepted</strong>" in html
    assert "<strong>01</strong>: Q0 --0--> Q2 --1--> Q3 => <strong>Rejected</strong>" in html
    assert "<strong>001</strong>: Q0 --0--> Q2 --0--> Q0 --1--> Q1 => <strong>Accepted</strong>" in html
    assert "<strong>0001</strong>:" in html and "Rejected" in html
    assert "<strong></strong>: Q0 => <strong>Rejected</strong>" in html
    
    # Test case 2
    # Alphabet: {p,f,h}
    # Language: Even p's, no pf, ends in h
    tc2_data = {
        "states": ["A", "B", "C", "D", "E", "F", "G"],
        "alphabet": ["p", "f", "h"],
        "start_state": "A",
        "accepting_states": ["B"],
        "state_meanings": {
            "A": "even #p, last symbol is neither p nor h (start, or just read f)",
            "B": "even #p, last symbol is h",
            "C": "even #p, last symbol is p",
            "D": "odd #p, last symbol is f",
            "E": "odd #p, last symbol is h",
            "F": "odd #p, last symbol is p",
            "G": "dead (a 'pf' has occurred)"
        },
        "transitions": {
            "A": {"p": "F", "f": "A", "h": "B"},
            "B": {"p": "F", "f": "A", "h": "B"},
            "C": {"p": "F", "f": "G", "h": "B"},
            "D": {"p": "C", "f": "D", "h": "E"},
            "E": {"p": "C", "f": "D", "h": "E"},
            "F": {"p": "C", "f": "G", "h": "E"},
            "G": {"p": "G", "f": "G", "h": "G"}
        },
        "strings": ["phfph", "ppfh"]
    }
    
    tc2_result = solve_universal("String Acceptance Traces", tc2_data)
    print("Test Case 2 Result generated.")
    
    html2 = tc2_result['subquestions'][0]['answer']
    assert "Accepted" in html2 and "phfph" in html2
    assert "Rejected" in html2 and "ppfh" in html2
    
    # Verify tables generated
    assert "<table border='1'>" in html
    assert "<th>Meaning</th>" in html
    assert "<td>Even 0s, ends in 1</td>" in html
    
    assert "<table border='1'>" in html2
    assert "<td>dead (a 'pf' has occurred)</td>" in html2
    
    print("All checks passed successfully.")
    
    generate_html([tc1_result, tc2_result], "output/mode_b_custom_tests.html")

if __name__ == "__main__":
    run_test_cases()
