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
    added_nodes = set()
    processed_pairs = set()
    
    # A. Process Spouses
    for p1, p2 in spouses_map.items():
        if p1 in relevant_nodes and p2 in relevant_nodes:
            pair = tuple(sorted((p1, p2)))
            if pair not in processed_pairs:
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    # P1
                    fill = '#FFD700' if p1 == center_node else '#E6F3FF'
                    s.node(p1, p1, shape='box', style='filled', fillcolor=fill, color='#2B7CE9')
                    added_nodes.add(p1)
                    # P2
                    fill = '#FFD700' if p2 == center_node else '#E6F3FF'
                    s.node(p2, p2, shape='box', style='filled', fillcolor=fill, color='#2B7CE9')
                    added_nodes.add(p2)
                    
                    s.edge(p1, p2, style='invis') 
                
                dot.edge(p1, p2, style='dashed', dir='none', color='#FF8888', constraint='false')
                processed_pairs.add(pair)

    # B. Add Remaining Nodes
    for node in relevant_nodes:
        if node not in added_nodes:
            fill = '#FFD700' if node == center_node else '#E6F3FF'
            dot.node(node, node, shape='box', style='filled', fillcolor=fill, color='#2B7CE9')
            added_nodes.add(node)


    # --- 3. Add Edges (Father -> Child Only) ---
    
    # Create a quick lookup for gender: { 'Name': 'M', ... }
    gender_map = {p.get('name'): p.get('gender', 'M') for p in data if p.get('name')}

    # Iterate through every node in the graph to find its parents
    for child in relevant_nodes:
        # --- CRITICAL FIX START ---
        # If a spouse was added to relevant_nodes but has no own record/edges, 
        # they won't be in G. We must skip them to prevent the NetworkXError.
        if child not in G:
            continue
        # --- CRITICAL FIX END ---

        # Get all parents (predecessors) for this child from the graph G
        parents = [p for p in G.predecessors(child) if p in relevant_nodes]
        
        if not parents:
            continue
            
        # Logic: Select which parent to draw the line from
        father_node = None
        
        # Priority 1: Find a male parent
        fathers = [p for p in parents if gender_map.get(p) == 'M']
        
        if fathers:
            father_node = fathers[0] # Use the father
        else:
            # Priority 2: Fallback to the first parent found
            father_node = parents[0]
            
        # Draw exactly ONE edge per child
        dot.edge(father_node, child, color='#555555')

    return dot
