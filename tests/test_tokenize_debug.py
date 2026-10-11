from solvers.cfg_solver import CFGSolver

s = CFGSolver("""S -> 'a b' | 'c d' | a | '0' | '1' | '(' | ')' | epsilon""", 'S')
print("Terminals:", s.terminals)
test_cases = [
    "( ( ) ) ( )",
    "(())()",
    "a a a",
    "aaa",
    "'a b' 'c d'",
    '"a b" a 0 1 ( )',
    "epsilon",
    "ε",
    "",
    "   ",
    ['(', ' ', ')'],
    ['( ( ) ) ( )']
]
for tc in test_cases:
    print(repr(tc), "->", s.tokenize_input(tc))
