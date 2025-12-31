import graphviz
import streamlit as st
import networkx as nx

def get_focused_subgraph(full_data, center_person_name):
    # ... (This logic remains the SAME as before) ...
    # It builds G, finds relevant_nodes, and spouses_map correctly.
    
    # --- RE-PASTING LOGIC FOR SAFETY ---
    G = nx.DiGraph()
    name_map = {p['name'].lower(): p['name'] for p in full_data if 'name' in p}
    center_name_key = center_person_name.lower().strip()
    
    if center_name_key not in name_map:
        return None, f"Person '{center_person_name}' not found."
    
    actual_center_name = name_map[center_name_key]
    
    for person in full_data:
        name = person.get('name')
        if not name: continue
        G.add_node(name)
        parents = person.get('parents', [])
        if isinstance(parents, str): parents = [parents]
        for parent in parents:
            if parent:
                G.add_edge(parent, name) 

    try:
        ancestors = nx.ancestors(G, actual_center_name)
        descendants = nx.descendants(G, actual_center_name)
        relevant_nodes = ancestors.union(descendants)
        relevant_nodes.add(actual_center_name)
        
        spouses_map = {}
        for person in full_data:
            name = person.get('name')
            if name in relevant_nodes:
                spouse = person.get('spouse')
                if spouse:
                    spouses_map[name] = spouse
                    relevant_nodes.add(spouse)
                    
        return relevant_nodes, actual_center_name, G, spouses_map
    except Exception as e:
        return None, str(e)


def render_focused_tree(data, center_name):
    result = get_focused_subgraph(data, center_name)
    if not result or len(result) == 2:
        st.error(result[1] if result else "Unknown Error")
        return None
        
    relevant_nodes, center_node, G, spouses_map = result

    # --- GRAPHVIZ DRAWING ---
    dot = graphviz.Digraph(comment='Family Tree')
    
    # 1. Global Attributes
    dot.attr(rankdir='TB')
    dot.attr(splines='ortho') 
    dot.attr(nodesep='0.6', ranksep='0.8')
    
    # 2. Add Nodes & Handle Spouses Grouping
    # We track which nodes we've already added to avoid duplicates
    added_nodes = set()

    # A. Process Spouses First (Force them to same rank)
    # We iterate through the map. Note: map might have A->B and B->A.
    processed_pairs = set()
    
    for p1, p2 in spouses_map.items():
        if p1 in relevant_nodes and p2 in relevant_nodes:
            pair = tuple(sorted((p1, p2)))
            if pair not in processed_pairs:
                # Create a subgraph for this pair to force same rank
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    
                    # Add P1
                    fill = '#FFD700' if p1 == center_node else '#E6F3FF'
                    s.node(p1, p1, shape='box', style='filled', fillcolor=fill, color='#2B7CE9')
                    added_nodes.add(p1)
                    
                    # Add P2
                    fill = '#FFD700' if p2 == center_node else '#E6F3FF'
                    s.node(p2, p2, shape='box', style='filled', fillcolor=fill, color='#2B7CE9')
                    added_nodes.add(p2)
                    
                    # Invisible edge to force ordering inside the rank (optional)
                    s.edge(p1, p2, style='invis') 
                
                # Draw the visible spouse connection
                dot.edge(p1, p2, style='dashed', dir='none', color='#FF8888', constraint='false')
                
                processed_pairs.add(pair)

    # B. Add Remaining Nodes (Single people without displayed spouses)
    for node in relevant_nodes:
        if node not in added_nodes:
            fill = '#FFD700' if node == center_node else '#E6F3FF'
            dot.node(node, node, shape='box', style='filled', fillcolor=fill, color='#2B7CE9')
            added_nodes.add(node)

    # 3. Add Edges (Parent -> Child)
    for parent, child in G.edges():
        if parent in relevant_nodes and child in relevant_nodes:
            dot.edge(parent, child, color='#555555')

    return dot
