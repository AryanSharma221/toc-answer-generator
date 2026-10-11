class DFASimulator:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = set(accepting_states)

    def validate(self):
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
            # Check for extra symbols in transitions
            for symbol in trans:
                if symbol not in self.alphabet:
                    return f"Transition from '{state}' on unknown symbol '{symbol}'."
        return None

    def simulate(self, input_string):
        # Handle explicit empty string designations
        if input_string.lower() in ["epsilon", "eps", "Îµ", "ε", ""]:
            input_string = ""
            
        trace_table = []
        state_sequence = [self.start_state]
        
        current_state = self.start_state
        error = None
        
        for char in input_string:
            if char not in self.alphabet:
                error = f"Input Validation Error: Symbol '{char}' is not in the alphabet {sorted(list(self.alphabet))}."
                break
            
            next_state = self.transitions.get(current_state, {}).get(char)
            if not next_state:
                error = f"Execution Error: Missing transition from state '{current_state}' on symbol '{char}'."
                break
                
            trace_table.append({
                "current": current_state,
                "symbol": char,
                "next": next_state
            })
            
            current_state = next_state
            state_sequence.append(current_state)
            
        accepted = (current_state in self.accepting_states) if not error else False
        
        return {
            "input_string": input_string,
            "accepted": accepted,
            "state_sequence": state_sequence,
            "trace_table": trace_table,
            "final_state": current_state,
            "error": error
        }
