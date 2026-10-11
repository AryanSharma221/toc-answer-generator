class NFAConverter:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = set(accepting_states)
        
        self.epsilon_symbols = {"", "eps", "epsilon", "\u03B5"} # Fixed encoding issue for epsilon

    def validate(self):
        if self.start_state not in self.states:
            return f"Start state '{self.start_state}' is not in states."
        for acc in self.accepting_states:
            if acc not in self.states:
                return f"Accepting state '{acc}' is not in states."
        
        for state in self.states:
            trans = self.transitions.get(state, {})
            for symbol, dests in trans.items():
                if symbol not in self.alphabet and symbol.lower() not in self.epsilon_symbols:
                    return f"Transition from '{state}' on unknown symbol '{symbol}'."
                if not isinstance(dests, list):
                    return f"Destinations for NFA transition from '{state}' on '{symbol}' must be a list (even if empty or single)."
                for d in dests:
                    if d not in self.states:
                        return f"Transition from '{state}' on '{symbol}' leads to unknown state '{d}'."
        return None

    def e_closure(self, states_set):
        closure = set(states_set)
        queue = list(states_set)
        while queue:
            curr = queue.pop(0)
            trans = self.transitions.get(curr, {})
            for sym, dests in trans.items():
                if sym.lower() in self.epsilon_symbols:
                    for d in dests:
                        if d not in closure:
                            closure.add(d)
                            queue.append(d)
        return frozenset(closure)

    def convert(self):
        steps = []
        
        # 1. Start subset
        start_subset = self.e_closure({self.start_state})
        
        queue = [start_subset]
        discovered = [start_subset]
        
        dfa_transitions_raw = {}
        
        while queue:
            current = queue.pop(0)
            dfa_transitions_raw[current] = {}
            
            for symbol in self.alphabet:
                dest_set = set()
                for s in current:
                    dests = self.transitions.get(s, {}).get(symbol, [])
                    dest_set.update(dests)
                    
                e_dest_set = self.e_closure(dest_set)
                dfa_transitions_raw[current][symbol] = e_dest_set
                
                if e_dest_set not in discovered:
                    discovered.append(e_dest_set)
                    queue.append(e_dest_set)
                    
        # 2. State Mapping
        def format_subset(subset):
            if not subset:
                return "\u2205" # Empty set character
            return "{" + ",".join(sorted(list(subset))) + "}"

        state_mapping = {}
        new_states = []
        for subset in discovered:
            name = format_subset(subset)
            state_mapping[subset] = name
            new_states.append(name)
            
        new_start = state_mapping[start_subset]
        new_accepting = []
        for subset in discovered:
            # If intersection is non-empty
            if set(subset).intersection(self.accepting_states):
                new_accepting.append(state_mapping[subset])
                
        new_transitions = {}
        for subset in discovered:
            s_name = state_mapping[subset]
            new_transitions[s_name] = {}
            for symbol in self.alphabet:
                d_subset = dfa_transitions_raw[subset][symbol]
                new_transitions[s_name][symbol] = state_mapping[d_subset]
                
        # Check for epsilon transitions
        has_eps = False
        for s, trans in self.transitions.items():
            for sym in trans.keys():
                if sym.lower() in self.epsilon_symbols:
                    has_eps = True
                    break
            if has_eps: break
            
        # Generate steps explanation
        if has_eps:
            steps.append(f"1. Computed epsilon closure of start state '{self.start_state}': {new_start}")
        else:
            steps.append(f"1. Start subset initialized from the NFA start state: {new_start}.")
            
        steps.append(f"2. Discovered {len(discovered)} unique DFA subsets via subset construction.")
        if format_subset(frozenset()) in new_states:
            steps.append("3. Empty subset \u2205 is reachable and acts as a dead state.")
            
        # 3. Diagnostic: Unreachable NFA States
        reachable_nfa_states = set()
        for subset in discovered:
            reachable_nfa_states.update(subset)
        unreachable_nfa_states = sorted(list(self.states - reachable_nfa_states))

        if unreachable_nfa_states:
            steps.append(f"Diagnostic: Identified unreachable NFA states: {', '.join(unreachable_nfa_states)}")

        return {
            "steps": steps,
            "subsets": [sorted(list(s)) for s in discovered],
            "state_mapping": {format_subset(s): sorted(list(s)) for s in discovered},
            "unreachable_nfa_states": unreachable_nfa_states,
            "states": new_states,
            "alphabet": sorted(list(self.alphabet)),
            "transitions": new_transitions,
            "start_state": new_start,
            "accepting_states": new_accepting
        }
