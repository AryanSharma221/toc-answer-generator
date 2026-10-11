import nltk
from nltk.parse import EarleyChartParser
from nltk.tree import Tree
import re

class CFGSolver:
    def __init__(self, productions_str, start_symbol, alphabet=None):
        if not productions_str or not str(productions_str).strip():
            raise ValueError("No productions found. Please provide at least one CFG production rule (e.g., 'S -> a S b | epsilon').")
            
        if not start_symbol or not str(start_symbol).strip():
            raise ValueError("Start symbol cannot be empty.")
        self.start_symbol = str(start_symbol).strip()

        lines = [l.strip() for l in productions_str.strip().split('\n') if l.strip()]
        if not lines:
            raise ValueError("No productions found. Please provide at least one CFG production rule (e.g., 'S -> a S b | epsilon').")

        # 1. First pass: parse lines, validate LHS, collect LHS nonterminals
        lhs_symbols = set()
        parsed_rules = []
        for line in lines:
            if '->' not in line:
                raise ValueError(f"Invalid production syntax: '{line}'. Each production must contain '->' separating the left-hand side non-terminal from right-hand side alternatives.")
            lhs_raw, rhs_raw = line.split('->', 1)
            lhs = lhs_raw.strip()
            if not lhs:
                raise ValueError(f"Invalid production syntax: '{line}'. Left-hand side non-terminal cannot be empty.")
            if not re.match(r'^[A-Z][A-Za-z0-9_]*$', lhs):
                raise ValueError(f"Invalid left-hand side non-terminal: '{lhs}'. Left-hand side must be an uppercase non-terminal symbol (e.g., 'S', 'A').")
            lhs_symbols.add(lhs)
            parsed_rules.append((lhs, rhs_raw.strip()))

        if self.start_symbol not in lhs_symbols:
            raise ValueError(f"Start symbol '{self.start_symbol}' is not defined as a non-terminal in the grammar.")

        # 2. Second pass: normalize alternatives, quote terminals, identify RHS nonterminals
        processed = []
        rhs_nonterminals = set()
        for lhs, rhs in parsed_rules:
            alts = rhs.split('|')
            new_alts = []
            for alt in alts:
                alt = alt.strip()
                if alt.lower() in ['epsilon', 'eps', 'ε', "''", '""', '']:
                    new_alts.append('')
                else:
                    tokens = []
                    # Quote-aware regex to extract parts while preserving quoted strings
                    parts = re.findall(r"'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"|\S+", alt)
                    for part in parts:
                        if (part.startswith("'") and part.endswith("'") and len(part) >= 2) or \
                           (part.startswith('"') and part.endswith('"') and len(part) >= 2):
                            unquoted = part[1:-1]
                            escaped = unquoted.replace("'", "\\'")
                            tokens.append(f"'{escaped}'")
                        elif part in lhs_symbols:
                            tokens.append(part)
                            rhs_nonterminals.add(part)
                        else:
                            # Could be concatenated like (S)S, aSb, or AB where A and B are uppercase nonterminals
                            pieces = re.findall(r'[A-Z]|[a-z0-9]+|.', part)
                            for p in pieces:
                                if p.isupper():
                                    tokens.append(p)
                                    rhs_nonterminals.add(p)
                                else:
                                    escaped_p = p.replace("'", "\\'")
                                    tokens.append(f"'{escaped_p}'")
                    new_alts.append(" ".join(tokens))
            processed.append(f"{lhs} -> {' | '.join(new_alts)}")

        self.undefined_nonterminals = sorted(rhs_nonterminals - lhs_symbols)
        self.grammar = nltk.CFG.fromstring("\n".join(processed))
        self.parser = EarleyChartParser(self.grammar)
        self.terminals = {str(sym) for prod in self.grammar.productions() for sym in prod.rhs() if not isinstance(sym, nltk.Nonterminal)}
        self.nonterminals = {prod.lhs().symbol() for prod in self.grammar.productions()}
        self.alphabet = self.parse_alphabet(alphabet)

    @staticmethod
    def parse_alphabet(alphabet_input):
        if not alphabet_input:
            return None
        if isinstance(alphabet_input, (set, frozenset)):
            res = {str(s).strip().strip("'\"") for s in alphabet_input if str(s).strip() and str(s).strip().lower() not in ['epsilon', 'eps', 'ε', "''", '""']}
            return res if res else None
        if isinstance(alphabet_input, (list, tuple)):
            res = set()
            for item in alphabet_input:
                s = str(item).strip().strip("'\"")
                if s and s.lower() not in ['epsilon', 'eps', 'ε', "''", '""']:
                    res.add(s)
            return res if res else None
        if isinstance(alphabet_input, str):
            s = alphabet_input.strip()
            if not s:
                return None
            res = set()
            if ',' in s:
                raw_parts = s.split(',')
            else:
                raw_parts = s.split()
            for part in raw_parts:
                token = part.strip().strip("'\"")
                if token and token.lower() not in ['epsilon', 'eps', 'ε', "''", '""']:
                    res.add(token)
            return res if res else None
        return None

    def validate_tokens(self, tokens):
        """
        Validates each token against the alphabet (or grammar terminals if no alphabet).
        Reports only genuine unknown symbols.
        Returns None if valid, or an error string if invalid symbols exist.
        """
        valid_symbols = set(self.alphabet) if self.alphabet is not None else set(self.terminals)
        unknown_symbols = []
        for token in tokens:
            if not token or token.isspace():
                continue
            if token.lower() in ['epsilon', 'eps', 'ε', "''", '""']:
                continue
            if token not in valid_symbols:
                if token not in unknown_symbols:
                    unknown_symbols.append(token)
        if unknown_symbols:
            words_str = ", ".join([f"'{sym}'" for sym in unknown_symbols])
            if len(unknown_symbols) == 1:
                return f"Symbol '{unknown_symbols[0]}' is outside the alphabet (Grammar does not cover some of the input words: {words_str})."
            else:
                return f"Symbols {unknown_symbols} are outside the alphabet (Grammar does not cover some of the input words: {words_str})."
        return None

    def tokenize_input(self, raw_input):
        """
        Tokenizes input into grammar terminal tokens:
        - Splits space-separated tokens.
        - Trims leading and trailing whitespace.
        - Ignores repeated whitespace.
        - Never treats token-separator spaces as terminals.
        - Handles lists, strings, empty strings, and epsilon.
        """
        if raw_input is None:
            return []
        if isinstance(raw_input, (list, tuple)):
            clean_items = [str(x).strip() for x in raw_input if str(x).strip()]
            if not clean_items:
                return []
            known = set(self.terminals)
            if self.alphabet:
                known.update(self.alphabet)
            tokens = []
            for item in clean_items:
                if item in known:
                    tokens.append(item)
                else:
                    tokens.extend(self.tokenize_string(item))
            return tokens
        return self.tokenize_string(str(raw_input))

    def tokenize_string(self, s):
        s = s.strip()
        if not s or s.lower() in ['epsilon', 'eps', 'ε', "''", '""']:
            return []
        # Quote-aware regex to extract tokens:
        # Preserves spaces inside quoted multi-character terminals
        raw_parts = re.findall(r"'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"|\S+", s)
        tokens = []
        for part in raw_parts:
            part = part.strip()
            if not part or part.lower() in ['epsilon', 'eps', 'ε', "''", '""']:
                continue
            if (part.startswith("'") and part.endswith("'") and len(part) >= 2) or \
               (part.startswith('"') and part.endswith('"') and len(part) >= 2):
                content = part[1:-1]
                if content and content.lower() not in ['epsilon', 'eps', 'ε']:
                    tokens.append(content)
            else:
                tokens.extend(self._tokenize_unspaced_part(part))
        return tokens

    def _tokenize_unspaced_part(self, part):
        part = part.strip()
        if not part or part.lower() in ['epsilon', 'eps', 'ε', "''", '""']:
            return []

        known = set(self.terminals)
        if self.alphabet:
            known.update(self.alphabet)
            
        if part in known:
            return [part]

        sorted_terms = sorted([t for t in known if t], key=len, reverse=True)
        tokens = []
        i = 0
        n = len(part)
        while i < n:
            matched = False
            for term in sorted_terms:
                if part.startswith(term, i):
                    tokens.append(term)
                    i += len(term)
                    matched = True
                    break
            if not matched:
                tokens.append(part[i])
                i += 1
        return tokens

    def get_detailed_derivation(self, tree, mode='leftmost'):
        """
        Generates step-by-step derivation dictionary.
        Supports both 'leftmost' and 'rightmost' expansions.
        Preserves terminal/nonterminal identity internally in each step.
        """
        mode = mode.lower()
        steps = []
        frontier = [tree]
        
        has_multichar = any(len(sym) > 1 for sym in self.terminals)
        
        def render_frontier(f):
            if not f: return "ε"
            items = [node.label() if isinstance(node, Tree) else str(node) for node in f]
            if has_multichar:
                return " ".join(items).replace('Îµ', 'ε')
            else:
                return "".join(items).replace('Îµ', 'ε')
            
        steps.append({
            "index": 0,
            "form": render_frontier(frontier),
            "sentential_symbols": [{"symbol": node.label() if isinstance(node, Tree) else str(node), "is_nonterminal": isinstance(node, Tree)} for node in frontier],
            "expanded": None,
            "expanded_pos": None,
            "production": None
        })
        
        step_idx = 1
        while True:
            idx = -1
            if mode == 'rightmost':
                for i in range(len(frontier)-1, -1, -1):
                    if isinstance(frontier[i], Tree):
                        idx = i
                        break
            else:
                for i in range(len(frontier)):
                    if isinstance(frontier[i], Tree):
                        idx = i
                        break
            if idx == -1: break
            node = frontier[idx]
            children = list(node)
            
            expanded_nt = node.label()
            expanded_pos = idx
            if len(children) == 0:
                rhs = "ε"
                rhs_symbols = []
            else:
                rhs = " ".join([c.label() if isinstance(c, Tree) else str(c) for c in children])
                rhs_symbols = [c.label() if isinstance(c, Tree) else str(c) for c in children]
            production = f"{expanded_nt} -> {rhs}"
            
            if len(children) == 0:
                frontier = frontier[:idx] + frontier[idx+1:]
            else:
                frontier = frontier[:idx] + children + frontier[idx+1:]
                
            steps.append({
                "index": step_idx,
                "form": render_frontier(frontier),
                "sentential_symbols": [{"symbol": n.label() if isinstance(n, Tree) else str(n), "is_nonterminal": isinstance(n, Tree)} for n in frontier],
                "expanded": expanded_nt,
                "expanded_pos": expanded_pos,
                "production": production,
                "rhs_symbols": rhs_symbols
            })
            step_idx += 1
            
        return steps

    def build_tree_from_derivation(self, steps, mode='leftmost'):
        """
        Constructs the parse tree from actual verified production applications.
        Maintains unique node identifiers so repeated S or A symbols do not overwrite one another.
        Preserves parent-child relationships and original production order.
        Displays epsilon productions correctly.
        Supports nested recursion, repeated nonterminals, and both leftmost and rightmost derivations.
        """
        if not steps:
            return None
            
        mode = mode.lower()
        node_counter = 0
        start_sym = self.grammar.start().symbol()
        root = {
            'id': f'node_{node_counter}',
            'label': start_sym,
            'children': []
        }
        node_counter += 1
        
        # Active non-terminal nodes in sentential form (ordered left-to-right)
        active_nt_nodes = [root]
        
        for s in steps[1:]:
            expanded_nt = s['expanded']
            rhs_symbols = s.get('rhs_symbols', [])
            production = s.get('production', '')
            
            if mode == 'rightmost':
                target_idx = len(active_nt_nodes) - 1
            else:
                target_idx = 0
                
            if target_idx < 0 or target_idx >= len(active_nt_nodes):
                raise ValueError(f"No active nonterminal available to expand {expanded_nt} at step {s['index']}")
                
            target_node = active_nt_nodes.pop(target_idx)
            if target_node['label'] != expanded_nt:
                raise ValueError(f"Mismatched nonterminal: expected {target_node['label']}, got {expanded_nt}")
                
            if not rhs_symbols or production.endswith('-> ε'):
                eps_leaf = {
                    'id': f'node_{node_counter}',
                    'label': 'ε',
                    'children': []
                }
                node_counter += 1
                target_node['children'].append(eps_leaf)
            else:
                new_nt_nodes = []
                for sym in rhs_symbols:
                    child_node = {
                        'id': f'node_{node_counter}',
                        'label': sym,
                        'children': []
                    }
                    node_counter += 1
                    target_node['children'].append(child_node)
                    if sym in self.nonterminals:
                        new_nt_nodes.append(child_node)
                        
                # Insert new non-terminals back into active_nt_nodes at target_idx
                active_nt_nodes[target_idx:target_idx] = new_nt_nodes
                
        return root

    def get_tree_terminal_yield(self, node):
        """
        Extracts terminal leaves from the tree in left-to-right order.
        Explicitly excludes epsilon leaves ('ε', 'eps', 'epsilon') from terminal yield.
        """
        if not node:
            return []
        leaves = []
        def traverse(n):
            children = n.get('children', [])
            if not children:
                label = str(n.get('label', '')).strip("'\"")
                if label.lower() not in ['ε', 'eps', 'epsilon', "''", '""']:
                    leaves.append(label)
            else:
                for child in children:
                    traverse(child)
        traverse(node)
        return leaves

    def verify_tree_terminal_yield(self, tree_node, target_tokens):
        """
        Verifies that the terminal yield of the tree exactly equals the input target tokens.
        Returns (is_valid: bool, error_msg: Optional[str])
        """
        if tree_node is None:
            return False, "Parse tree is None"
        tree_yield = self.get_tree_terminal_yield(tree_node)
        clean_target = [str(t).strip("'\"") for t in target_tokens if str(t).lower() not in ['epsilon', 'eps', 'ε', "''", '""']]
        if tree_yield != clean_target:
            return False, f"Parse tree terminal yield mismatch: tree produced {tree_yield} but expected {clean_target}"
        return True, None

    def build_canonical_derivation(self, tree, tokens, mode='leftmost'):
        """
        Creates one canonical structured derivation result containing:
        - Grammar productions.
        - Start symbol.
        - Original target tokens.
        - Derivation mode.
        - Ordered sentential forms.
        - Production applied at each step.
        - Expanded nonterminal position.
        - Success/failure status.
        - Parse-tree data constructed from verified production applications.
        """
        steps = self.get_detailed_derivation(tree, mode=mode)
        
        clean_target = [t for t in tokens if t.lower() not in ['epsilon', 'eps', 'ε', "''", '""']]
        has_multichar = any(len(sym) > 1 for sym in self.terminals)
        target_str = " ".join(clean_target) if has_multichar else "".join(clean_target)
        if not target_str:
            target_str = "ε"
            
        final_form = steps[-1]["form"] if steps else ""
        terminal_yield = final_form
        
        grammar_prods = [f"{p.lhs()} -> {' '.join([repr(t) if isinstance(t, str) else str(t) for t in p.rhs()])}" for p in self.grammar.productions()]
        
        ordered_forms = [s["form"] for s in steps]
        
        # Derivation sequence in requested formats:
        # S
        # => (S)S
        # => ((S)S)S
        # ...
        derivation_sequence_text = "\n".join([ordered_forms[0]] + [f"=> {f}" for f in ordered_forms[1:]])
        derivation_sequence_math = " ⇒ ".join(ordered_forms)
        
        production_history = []
        for s in steps[1:]:
            production_history.append({
                "step": s["index"],
                "expanded": s["expanded"],
                "expanded_pos": s["expanded_pos"],
                "production": s["production"],
                "result_form": s["form"]
            })
            
        # Construct parse tree directly from verified derivation steps
        parse_tree_data = self.build_tree_from_derivation(steps, mode=mode)
        is_tree_valid, tree_err = self.verify_tree_terminal_yield(parse_tree_data, tokens)
        
        if not is_tree_valid:
            parse_tree_verified = False
            parse_tree_error = tree_err
            parse_tree_data = None
        else:
            parse_tree_verified = True
            parse_tree_error = None
        
        return {
            "grammar_productions": grammar_prods,
            "start_symbol": self.grammar.start().symbol(),
            "target_tokens": list(tokens),
            "target_string": target_str,
            "derivation_mode": mode.capitalize(),
            "status": "Accepted",
            "success": True,
            "failure_reason": None,
            "steps": steps,
            "ordered_sentential_forms": ordered_forms,
            "derivation_sequence_text": derivation_sequence_text,
            "derivation_sequence_math": derivation_sequence_math,
            "terminal_yield": terminal_yield,
            "production_history": production_history,
            "parse_tree_data": parse_tree_data,
            "parse_tree_verified": parse_tree_verified,
            "parse_tree_error": parse_tree_error
        }

    def build_failed_derivation(self, tokens, reason, mode='leftmost', status='Rejected'):
        """
        Creates a failed canonical derivation result.
        """
        clean_target = [t for t in tokens if t.lower() not in ['epsilon', 'eps', 'ε', "''", '""']]
        has_multichar = any(len(sym) > 1 for sym in self.terminals)
        target_str = " ".join(clean_target) if has_multichar else "".join(clean_target)
        if not target_str:
            target_str = "ε"
            
        grammar_prods = [f"{p.lhs()} -> {' '.join([repr(t) if isinstance(t, str) else str(t) for t in p.rhs()])}" for p in self.grammar.productions()]
        
        return {
            "grammar_productions": grammar_prods,
            "start_symbol": self.grammar.start().symbol(),
            "target_tokens": list(tokens),
            "target_string": target_str,
            "derivation_mode": mode.capitalize(),
            "status": status,
            "success": False,
            "failure_reason": reason,
            "steps": [],
            "ordered_sentential_forms": [],
            "derivation_sequence_text": "",
            "derivation_sequence_math": "",
            "terminal_yield": None,
            "production_history": [],
            "parse_tree_data": None
        }

    def get_leftmost_derivation(self, tree):
        steps = self.get_detailed_derivation(tree, mode='leftmost')
        return [s['form'] for s in steps]

    def get_rightmost_derivation(self, tree):
        steps = self.get_detailed_derivation(tree, mode='rightmost')
        return [s['form'] for s in steps]

    def validate_derivation(self, steps, target_tokens, mode='leftmost', tree=None):
        if not steps:
            return "Derivation is empty."
        if isinstance(steps[0], dict):
            start_form = steps[0]['form']
            final_form = steps[-1]['form']
            forms = [s['form'] for s in steps]
        else:
            start_form = steps[0]
            final_form = steps[-1]
            forms = steps
            
        if start_form != self.grammar.start().symbol():
            return f"First step '{start_form}' does not match start symbol '{self.grammar.start().symbol()}'."
            
        clean_target = [t for t in target_tokens if t.lower() not in ['epsilon', 'eps', 'ε', "''", '""']]
        has_multichar = any(len(sym) > 1 for sym in self.terminals)
        if has_multichar:
            target_str = " ".join(clean_target)
        else:
            target_str = "".join(clean_target)
        
        # Check that final form has no non-terminals
        for nt in self.nonterminals:
            if nt not in self.terminals and nt in final_form:
                return f"Final sentential form '{final_form}' still contains unexpanded non-terminal '{nt}'."

        if not clean_target:
            if final_form not in ['ε', '']:
                return f"Final step '{final_form}' does not match empty target string (expected 'ε')."
        else:
            if has_multichar:
                if final_form != target_str:
                    return f"Final step '{final_form}' does not match target string '{target_str}'."
            else:
                final_clean = final_form.replace(' ', '')
                if final_clean != target_str:
                    return f"Final step '{final_form}' does not match target string '{target_str}'."
                
        # Validate adjacent steps: each adjacent pair must differ by exactly one production application
        for i in range(len(forms) - 1):
            if forms[i] == forms[i+1]:
                return f"Step {i} and {i+1} are identical, indicating no production was applied."
                
        # Check parse tree leaves if tree provided
        if tree is not None:
            leaves = [l for l in tree.leaves() if l.lower() not in ['epsilon', 'eps', 'ε', "''", '""']]
            leaf_str = " ".join(leaves) if has_multichar else "".join(leaves)
            if leaf_str != target_str:
                return f"Parse tree leaves '{leaf_str}' do not match target string '{target_str}'."
                
        return None

    def explain_structural_difference(self, tree1, tree2):
        prods1 = tree1.productions()
        prods2 = tree2.productions()
        
        for i in range(min(len(prods1), len(prods2))):
            if prods1[i] != prods2[i]:
                diff1 = prods1[i]
                diff2 = prods2[i]
                return f"The trees diverge structurally. In a pre-order traversal, Tree 1 applies the rule <code>{diff1}</code> at a specific node, whereas Tree 2 applies the rule <code>{diff2}</code> at that same position. This proves the grammar allows the same tokens to be grouped under different hierarchical meanings."
        return "The trees have identical production lists but differ in branching structure."

    def parse(self, input_tokens, max_trees=100, timeout=5.0, max_tokens=300):
        try:
            tokens = self.tokenize_input(input_tokens)
            if len(tokens) > max_tokens:
                return f"Search incomplete: Input length ({len(tokens)} tokens) exceeds resource limit of {max_tokens} tokens."
                
            val_err = self.validate_tokens(tokens)
            if val_err:
                return val_err
                
            if self.undefined_nonterminals:
                return f"The string is not generated by the grammar (Grammar contains undefined non-terminal(s): {', '.join(self.undefined_nonterminals)})."
                
            # Boundary normalization for parser library (nltk.parse.EarleyChartParser)
            parser_input = list(tokens)
            assert not any(t.isspace() or t == '' for t in parser_input), "Parser input contains whitespace tokens"
                
            import time
            start_time = time.time()
            tree_generator = self.parser.parse(parser_input)
            trees = []
            for t in tree_generator:
                trees.append(t)
                if len(trees) >= max_trees:
                    break
                if time.time() - start_time > timeout:
                    if not trees:
                        return f"Search incomplete: Derivation search timed out after {timeout}s before completing parse."
                    break
            return trees
        except (RecursionError, MemoryError) as e:
            return f"Search incomplete: Resource limits exceeded during derivation search ({type(e).__name__})."
        except ValueError as e:
            return str(e)
            
    def is_ambiguous(self, input_tokens):
        trees = self.parse(input_tokens)
        if isinstance(trees, str):
            return False, trees
        return len(trees) > 1, trees

    def format_tree_for_renderer(self, nltk_tree, node_id=None):
        if node_id is None:
            node_id = [0]
        # Convert NLTK tree to our graphviz format
        current_id = str(node_id[0])
        node_id[0] += 1
        
        node = {
            'id': current_id,
            'label': nltk_tree.label() if isinstance(nltk_tree, Tree) else nltk_tree
        }
        
        if isinstance(nltk_tree, Tree):
            node['children'] = []
            if len(nltk_tree) == 0:
                # Epsilon production: add an explicit epsilon leaf
                eps_id = str(node_id[0])
                node_id[0] += 1
                node['children'].append({'id': eps_id, 'label': 'ε'})
            else:
                for child in nltk_tree:
                    node['children'].append(self.format_tree_for_renderer(child, node_id))
                
        return node
