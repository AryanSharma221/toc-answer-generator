class DFAMinimizer:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = list(states)
        self.alphabet = list(alphabet)
        self.transitions = {s: {a: dest for a, dest in trans.items()} for s, trans in transitions.items()}
        self.start_state = start_state
        self.accepting_states = set(accepting_states)

    def validate(self):
        if not self.states:
            return "State set cannot be empty."
        if len(self.states) != len(set(self.states)):
            return "Duplicate states found."
        if self.start_state not in self.states:
            return f"Start state '{self.start_state}' is not in states."
        for acc in self.accepting_states:
            if acc not in self.states:
                return f"Accepting state '{acc}' is not in states."
        for state in self.states:
            if state not in self.transitions:
                return f"State '{state}' has no defined transitions."
            trans = self.transitions[state]
            for symbol in self.alphabet:
                if symbol not in trans:
                    return f"Missing transition for state '{state}' on symbol '{symbol}'."
                dest = trans[symbol]
                if dest not in self.states:
                    return f"Transition from '{state}' on '{symbol}' leads to unknown state '{dest}'."
            for symbol in trans:
                if symbol not in self.alphabet:
                    return f"Invalid transition symbol '{symbol}' for state '{state}'."
        return None

    def minimize(self):
        steps = []
        
        # 1. Reachability
        reachable = set([self.start_state])
        queue = [self.start_state]
        while queue:
            curr = queue.pop(0)
            for a in self.alphabet:
                dest = self.transitions.get(curr, {}).get(a)
                if dest and dest not in reachable:
                    reachable.add(dest)
                    queue.append(dest)
                    
        unreachable = set(self.states) - reachable
        if unreachable:
            steps.append(f"Unreachable states removed: {', '.join(sorted(list(unreachable)))}")
        else:
            steps.append("No unreachable states found.")
            
        reachable_states = sorted(list(reachable))
        reachable_acc = set(self.accepting_states).intersection(reachable)
        reachable_non_acc = set(reachable) - reachable_acc

        # 2. Partitions
        # Initial partition: F and Q \ F
        P = []
        if reachable_acc: P.append(sorted(list(reachable_acc)))
        if reachable_non_acc: P.append(sorted(list(reachable_non_acc)))
        
        # Format partition nicely
        def format_P(part_list):
            return "{" + ", ".join(["{" + ",".join(g) + "}" for g in part_list]) + "}"
            
        steps.append(f"Initial partitions: {format_P(P)}")

        changed = True
        while changed:
            changed = False
            new_P = []
            for group in P:
                if len(group) <= 1:
                    new_P.append(group)
                    continue
                
                # group states by signature
                # signature of q is a tuple: (dest_group_index_for_a1, dest_group_index_for_a2, ...)
                def get_group_index(state, partitions):
                    for i, g in enumerate(partitions):
                        if state in g: return i
                    return -1
                    
                signatures = {}
                for q in group:
                    sig = []
                    for a in self.alphabet:
                        dest = self.transitions[q][a]
                        sig.append(get_group_index(dest, P))
                    sig = tuple(sig)
                    if sig not in signatures:
                        signatures[sig] = []
                    signatures[sig].append(q)
                
                for sig, members in signatures.items():
                    new_P.append(members)
                
                if len(signatures) > 1:
                    changed = True
                    
            P = sorted(new_P, key=lambda g: g[0])

        steps.append(f"Final partitions: {format_P(P)}")

        steps.append(f"Final Partition: {format_P(P)}")
        equivalent_classes = [g for g in P if len(g) > 1]
        if equivalent_classes:
            steps.append(f"Nontrivial merged classes: {format_P(equivalent_classes)}")
        else:
            steps.append("Nontrivial merged classes: None (No equivalent states to merge)")
            
        # 3. Construct Minimized DFA
        new_states = []
        state_map = {}
        for group in P:
            name = group[0] if len(group) == 1 else "{" + ",".join(group) + "}"
            new_states.append(name)
            for s in group:
                state_map[s] = name
                
        new_start = state_map[self.start_state]
        new_acc = set([state_map[s] for s in reachable_acc])
        
        new_transitions = {}
        for group in P:
            rep = group[0]
            new_s = state_map[rep]
            new_transitions[new_s] = {}
            for a in self.alphabet:
                dest = self.transitions[rep][a]
                new_transitions[new_s][a] = state_map[dest]
                
        steps.append(f"Final state count: {len(new_states)}")

        return {
            "steps": steps,
            "states": new_states,
            "alphabet": self.alphabet,
            "transitions": new_transitions,
            "start_state": new_start,
            "accepting_states": list(new_acc),
            "unreachable": list(unreachable),
            "partitions": P
        }
