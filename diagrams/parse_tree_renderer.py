import graphviz
import os
import uuid

os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

def render_parse_tree(root_node, filename='parse_tree', directory='output/figures'):
    """
    root_node format:
    {
        'id': '0',
        'label': 'D',
        'children': [
            {'id': '1', 'label': 'C', 'children': [...]},
            {'id': '2', 'label': 'D', 'children': [...]}
        ]
    }
    """
    os.makedirs(directory, exist_ok=True)
    dot = graphviz.Digraph(format='png')
    dot.attr(ordering='out') # ensure left-to-right order is preserved
    dot.attr('node', shape='none')

    def add_nodes_edges(node):
        if 'id' not in node:
            node['id'] = str(uuid.uuid4())
            
        label_str = str(node.get('label', ''))
        # safely handle mojibake and standard epsilon representations
        if label_str in ['Îµ', '\u03b5', 'ÃŽÂµ', 'epsilon', 'ε']:
            dot.node(node['id'], '<&epsilon;>')
        else:
            dot.node(node['id'], label_str)
            
        if 'children' in node:
            for child in node['children']:
                add_nodes_edges(child)
                dot.edge(node['id'], child['id'])

    add_nodes_edges(root_node)

    output_path = os.path.join(directory, filename)
    try:
        dot.render(output_path, cleanup=True)
        return output_path + '.png'
    except graphviz.backend.execute.ExecutableNotFound:
        raise RuntimeError("Graphviz is not installed or not found on PATH. Please install Graphviz to generate parse trees.")
    except Exception as e:
        raise RuntimeError(f"Parse tree diagram generation failed: {str(e)}")
