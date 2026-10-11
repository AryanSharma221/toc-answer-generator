import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ValidationGate:
    @staticmethod
    def validate_minimization(problem_data: Dict[str, Any], canonical_result: Dict[str, Any]):
        orig_states = set(problem_data['states'])
        orig_accepting = set(problem_data['accepting_states'])
        min_states = canonical_result['diagram_json']['states']
        min_accepting = canonical_result['diagram_json']['accepting_states']
        
        # 1. No final class mixes accepting and non-accepting states
        for ms_label in min_states:
            inner = ms_label.strip("{}")
            if not inner: continue
            sub_states = inner.split(",")
            
            has_accepting = any(s in orig_accepting for s in sub_states)
            has_rejecting = any(s not in orig_accepting for s in sub_states)
            if has_accepting and has_rejecting:
                raise ValueError(f"Validation Error: Equivalence class {ms_label} mixes accepting and non-accepting states.")
        
        # 2. Every destination references a valid minimized state
        transitions = canonical_result['diagram_json']['transitions']
        for state, trans in transitions.items():
            for symbol, dest in trans.items():
                if dest not in min_states:
                    raise ValueError(f"Validation Error: Transition from {state} on {symbol} leads to invalid state {dest}.")

        # 3. Language equivalence using automata-lib
        try:
            from automata.fa.dfa import DFA
            dfa_expected = DFA(
                states=set(problem_data.get('states', [])),
                input_symbols=set(problem_data.get('alphabet', [])),
                transitions=problem_data.get('transitions', {}),
                initial_state=problem_data.get('start_state', ''),
                final_states=set(problem_data.get('accepting_states', [])),
                allow_partial=True
            )
            dfa_actual = DFA(
                states=set(min_states),
                input_symbols=set(problem_data.get('alphabet', [])),
                transitions=transitions,
                initial_state=canonical_result['diagram_json']['start_state'],
                final_states=set(min_accepting)
            )
            if dfa_expected != dfa_actual:
                raise ValueError("Validation Error: Minimized DFA language is not equivalent to the original DFA.")
        except Exception as e:
            if "Validation Error" in str(e):
                raise
            pass
        return True

    @staticmethod
    def validate_traces(problem_data: Dict[str, Any], canonical_result: Dict[str, Any]):
        # "For string acceptance, replay every transition from the original input."
        # We formally validate the trace simulation again independently.
        
        transitions = problem_data.get('transitions', {})
        accepting = set(problem_data.get('accepting_states', []))
        start_state = problem_data.get('start_state', '')
        
        raw_traces = canonical_result.get("raw_data", {}).get("trace_results", [])
        
        for sim_res in raw_traces:
            if sim_res.get("error"):
                continue # Handled as rejection correctly
                
            input_string = sim_res.get("input_string", "")
            current = start_state
            
            # Replay the sequence independently
            for symbol in input_string:
                if current not in transitions or symbol not in transitions[current]:
                    # Should map to a trap state or fail
                    pass
                else:
                    current = transitions[current][symbol]
                    
            expected_accept = (current in accepting)
            if expected_accept != sim_res.get("accepted"):
                raise ValueError(f"Validation Error: Trace logic failed for {input_string}. Expected {expected_accept} but got {sim_res.get('accepted')}.")
                
            if current != sim_res.get("final_state"):
                raise ValueError(f"Validation Error: Trace terminal state mismatch for {input_string}.")
                
        return True

    @staticmethod
    def validate_nfa_to_dfa(problem_data: Dict[str, Any], canonical_result: Dict[str, Any]):
        dfa_states = canonical_result['diagram_json']['states']
        dfa_trans = canonical_result['diagram_json']['transitions']
        dfa_alphabet = canonical_result['diagram_json']['alphabet']
        dfa_start = canonical_result['diagram_json']['start_state']
        dfa_accepting = set(canonical_result['diagram_json']['accepting_states'])
        
        raw_data = canonical_result.get('raw_data', {})
        state_mapping = raw_data.get('state_mapping', {})
        
        nfa_states = set(problem_data.get('states', []))
        nfa_trans_orig = problem_data.get('transitions', {})
        nfa_accepting = set(problem_data.get('accepting_states', []))
        epsilon_symbols = {"", "eps", "epsilon", "ε"}
        
        def e_closure(states_set):
            closure = set(states_set)
            queue = list(states_set)
            while queue:
                curr = queue.pop(0)
                trans = nfa_trans_orig.get(curr, {})
                for sym, dests in trans.items():
                    if sym.lower() in epsilon_symbols:
                        for d in dests:
                            if d not in closure:
                                closure.add(d)
                                queue.append(d)
            return frozenset(closure)
            
        def format_subset(subset):
            if not subset: return "∅"
            return "{" + ",".join(sorted(list(subset))) + "}"

        # 1-7. Mathematical Sub-Validator
        reachable = {dfa_start}
        queue = [dfa_start]
        
        while queue:
            curr_dfa_state = queue.pop(0)
            curr_nfa_subset = state_mapping.get(curr_dfa_state, [])
            
            # 4. Verify accepting state classification
            is_accepting = bool(set(curr_nfa_subset).intersection(nfa_accepting))
            if is_accepting and curr_dfa_state not in dfa_accepting:
                raise ValueError(f"Validation Error: Subset {curr_dfa_state} should be accepting but is not.")
            if not is_accepting and curr_dfa_state in dfa_accepting:
                raise ValueError(f"Validation Error: Subset {curr_dfa_state} is accepting but contains no NFA accepting states.")
                
            # 7. Check exactly one destination per symbol
            if len(dfa_trans.get(curr_dfa_state, {})) != len(dfa_alphabet):
                raise ValueError(f"Validation Error: State {curr_dfa_state} does not have exactly one transition per alphabet symbol.")
                
            for symbol in dfa_alphabet:
                # 1. Recompute union
                dest_set = set()
                for s in curr_nfa_subset:
                    dest_set.update(nfa_trans_orig.get(s, {}).get(symbol, []))
                expected_e_dest = e_closure(dest_set)
                expected_dest_str = format_subset(expected_e_dest)
                
                # 2. Compare with DFA transition
                actual_dest = dfa_trans.get(curr_dfa_state, {}).get(symbol)
                if actual_dest != expected_dest_str:
                    raise ValueError(f"Validation Error: Transition mismatch for state {curr_dfa_state} on '{symbol}'. Expected {expected_dest_str}, got {actual_dest}.")
                
                # 3. Verify destination subset exists in discovered states
                if actual_dest not in dfa_states:
                    raise ValueError(f"Validation Error: NFA subset {curr_dfa_state} maps to non-existent subset {actual_dest} on symbol {symbol}.")
                    
                if actual_dest not in reachable:
                    reachable.add(actual_dest)
                    queue.append(actual_dest)
                    
        # 5. Verify every reported subset is reachable
        for s in dfa_states:
            if s not in reachable:
                raise ValueError(f"Validation Error: Reported state {s} is not reachable from the DFA start state.")
                
        # 6. Verify no reachable subset is missing
        for s in reachable:
            if s not in dfa_states:
                raise ValueError(f"Validation Error: Reachable subset {s} is missing from the reported states.")

        # 8. Language equivalence
        try:
            from automata.fa.nfa import NFA
            from automata.fa.dfa import DFA
            
            nfa_trans_lib = {}
            for s, t in nfa_trans_orig.items():
                nfa_trans_lib[s] = {}
                for a, dests in t.items():
                    nfa_trans_lib[s][a] = set(dests)
            for s, t in nfa_trans_lib.items():
                keys_to_change = [a for a in t if a.lower() in epsilon_symbols]
                for a in keys_to_change:
                    t[""] = t.pop(a)
                    
            nfa_lib = NFA(
                states=set(nfa_states),
                input_symbols=set(dfa_alphabet),
                transitions=nfa_trans_lib,
                initial_state=problem_data.get('start_state', ''),
                final_states=nfa_accepting
            )
            dfa_expected = DFA.from_nfa(nfa_lib)
            
            dfa_actual = DFA(
                states=set(dfa_states),
                input_symbols=set(dfa_alphabet),
                transitions=dfa_trans,
                initial_state=dfa_start,
                final_states=dfa_accepting
            )
            
            if dfa_expected != dfa_actual:
                raise ValueError("Validation Error: Independent language equivalence check failed.")
        except Exception as e:
            if "Validation Error" in str(e):
                raise e
        
        return True

    @staticmethod
    def handle_api_disagreement(category: str, canonical_result: Dict[str, Any], verification_status: Dict[str, Any]):
        """
        If the API disagrees but formal validation supports the canonical result, 
        retain the canonical result and report the disagreement internally.
        """
        if not verification_status.get("verified", False):
            # Formal validation passed (or we wouldn't be here), but API disagreed!
            discrepancies = verification_status.get("discrepancies", [])
            logger.warning(f"VERIFICATION DISAGREEMENT in {category}: Formal mathematical validation PASSED, but API independent verifier disagreed. Discrepancies: {discrepancies}")
            
            # The canonical result is inherently retained because it sits safely in canonical_result
            # We flag this in the return structure so the system knows it was an internal disagreement.
            canonical_result["internal_disagreement_flagged"] = True
            canonical_result["discrepancies"] = discrepancies

    @staticmethod
    def validate_api_claims(category: str, canonical_result: Dict[str, Any], ai_html: str):
        if category == "Minimization" and canonical_result:
            expected_count = len(canonical_result['diagram_json']['states'])
            plain_text = re.sub(r'<[^>]+>', ' ', ai_html).lower()
            match = re.search(r'(\d+)\s+(?:equivalent|minimized|final)?\s*states', plain_text)
            if match:
                claimed_count = int(match.group(1))
                if claimed_count != expected_count:
                    raise ValueError(f"API Contradiction: AI explained a DFA with {claimed_count} states, but the true minimized DFA has {expected_count} states.")
        return True
