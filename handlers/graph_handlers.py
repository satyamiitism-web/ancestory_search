import graphviz

def render_graph(relatives):
    g = graphviz.Digraph(comment='Family Tree')
    g.attr(rankdir='TB', splines='ortho')
    g.attr('node', shape='rect', style='filled', fontname='Helvetica', penwidth='0', margin='0.2')
    g.attr('edge', color='#555555', penwidth='1.2', arrowhead='none')

    # Styles
    def get_color(person):
        if person['name'] == relatives['target']['name']: return '#FFD54F' # Gold
        return '#F8BBD0' if person.get('gender') == 'F' else '#BBDEFB' # Pink/Blue

    def add_person(p):
        g.node(p['name'], label=p['name'], fillcolor=get_color(p))

    # Add Nodes
    target = relatives['target']
    add_person(target)
    
    if relatives['spouse']: add_person(relatives['spouse'])
    for p in relatives['parents']: add_person(p)
    for gp in relatives['grandparents']: add_person(gp)
    for c in relatives['children']: add_person(c)

    # --- CONNECTIONS ---

    # 1. Grandparents -> Parents
    for parent in relatives['parents']:
        gps = [gp for gp in relatives['grandparents'] if gp['name'] in parent.get('parents', [])]
        if gps:
            union_id = f"union_{parent['name']}_gps"
            g.node(union_id, shape='point', width='0.05')
            for gp in gps: g.edge(gp['name'], union_id)
            g.edge(union_id, parent['name'])

    # 2. Parents -> Target
    if relatives['parents']:
        union_id = "union_target_parents"
        g.node(union_id, shape='point', width='0.05')
        for p in relatives['parents']: g.edge(p['name'], union_id)
        g.edge(union_id, target['name'])

    # 3. Target + Spouse (The Fix)
    if relatives['spouse']:
        # Always create a union node if there is a spouse
        marriage_id = f"union_{target['name']}"
        g.node(marriage_id, shape='point', width='0.05', height='0.05', color='#333333')

        # Connect both to the marriage point
        g.edge(target['name'], marriage_id)
        g.edge(relatives['spouse']['name'], marriage_id)

        # Force side-by-side layout
        with g.subgraph() as s:
            s.attr(rank='same')
            s.node(target['name'])
            s.node(relatives['spouse']['name'])

        # 4. Connect Children to that Marriage Node
        if relatives['children']:
            for child in relatives['children']:
                g.edge(marriage_id, child['name'])
    
    # Fallback: If no spouse but has children (Single parent)
    elif relatives['children']:
        for child in relatives['children']:
            g.edge(target['name'], child['name'])

    return g
