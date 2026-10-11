import graphviz
import os

os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

def validate_dfa_diagram_data(dfa):
    required_keys = ['states', 'alphabet', 'transitions', 'start_state', 'accepting_states']
    for k in required_keys:
        if k not in dfa:
            raise ValueError(f"Invalid DFA data: missing key '{k}'")
            
    if not isinstance(dfa['states'], (list, set, tuple)):
        raise ValueError("Invalid DFA data: 'states' must be a collection")
        
    if not isinstance(dfa['transitions'], dict):
        raise ValueError("Invalid DFA data: 'transitions' must be a dictionary")
        
    if dfa['start_state'] not in dfa['states']:
        raise ValueError("Invalid DFA data: 'start_state' must be in 'states'")

def validate_rendered_diagram(output_path):
    if not os.path.exists(output_path):
        raise RuntimeError(f"Rendering failed: Output file {output_path} not found.")
    if os.path.getsize(output_path) == 0:
        raise RuntimeError(f"Rendering failed: Output file {output_path} is empty.")
    return True

def render_dfa_diagram(dfa, filename='dfa', directory='output/figures'):
    validate_dfa_diagram_data(dfa)
    
    os.makedirs(directory, exist_ok=True)
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', splines='true', overlap='false', ranksep='1.2', nodesep='0.8')
    # Improve layout and spacing
    # Improved layout already added above

    states = dfa['states']
    accepting_states = set(dfa['accepting_states'])
    start_state = dfa['start_state']
    if isinstance(start_state, list): start_state = start_state[0]
    transitions = dfa['transitions']

    # Add states
    for state in states:
        shape = 'doublecircle' if state in accepting_states else 'circle'
        dot.node(state, state, shape=shape)

    # Initial state arrow
    dot.node('__start__', '', shape='none', width='0', height='0')
    dot.edge('__start__', start_state)

    # Add transitions - Group multiple symbols going to the same destination
    for src in transitions:
        if src not in states: continue
        dest_map = {}
        for symbol, dest in transitions[src].items():
            dest_list = dest if isinstance(dest, list) else [dest]
            for d in dest_list:
                if d not in dest_map:
                    dest_map[d] = []
                dest_map[d].append(symbol)
            
        for dest, symbols in dest_map.items():
            label = ", ".join(sorted(symbols))
            dot.edge(src, dest, label=label)

    output_path = os.path.join(directory, filename)
    try:
        dot.render(output_path, cleanup=True)
        final_path = output_path + '.png'
        validate_rendered_diagram(final_path)
        return final_path
    except graphviz.backend.execute.ExecutableNotFound:
        raise RuntimeError("Graphviz is not installed or not found on PATH. Please install Graphviz to generate diagrams.")
    except Exception as e:
        if isinstance(e, RuntimeError) and "Rendering failed" in str(e):
            raise e
        raise RuntimeError(f"Diagram generation failed: {str(e)}")
