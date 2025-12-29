import graphviz


def render_graph(relatives):
    """Creates a graphviz chart focused on the target person"""
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB')

    # helper to style nodes
    def add_node(p, style="filled"):
        color = "#D1C4E9" if p['gender'] == 'F' else "#BBDEFB" # Pink/Blue-ish
        if p['name'] == relatives['target']['name']:
            color = "#FFEB3B" # Highlight target in Yellow
        graph.node(p['name'], label=p['name'], shape="box", style="filled", fillcolor=color)

    # 1. Add Target & Spouse
    target = relatives['target']
    add_node(target)

    if relatives['spouse']:
        spouse = relatives['spouse']
        add_node(spouse)
        # Draw double-headed arrow for marriage
        graph.edge(target['name'], spouse['name'], dir="both", color="red", label="Spouse")
        # Enforce same rank
        with graph.subgraph() as s:
            s.attr(rank='same')
            s.node(target['name'])
            s.node(spouse['name'])

    # 2. Add Parents
    for parent in relatives['parents']:
        add_node(parent)
        graph.edge(parent['name'], target['name'], label="Parent")

    # 3. Add Grandparents
    for gp in relatives['grandparents']:
        add_node(gp)
        # Connect GP to the correct parent
        # We have to check which parent is the child of this GP
        for parent in relatives['parents']:
            if gp['name'] in parent['parents']:
                graph.edge(gp['name'], parent['name'], label="Parent")

    for child in relatives['children']:
        add_node(child)
        # Draw edge from Target -> Child
        graph.edge(target['name'], child['name'])
        # If spouse exists, also draw edge from Spouse -> Child (optional, but looks better)
        if relatives['spouse']:
            graph.edge(relatives['spouse']['name'], child['name'])

    return graph
