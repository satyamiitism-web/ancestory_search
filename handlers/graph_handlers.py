import graphviz
import streamlit as st
import networkx as nx


def get_focused_subgraph(full_data, center_person_name):
    G = nx.DiGraph()
    name_map = {p['name'].lower(): p['name'] for p in full_data if 'name' in p}
    center_name_key = center_person_name.lower().strip()
    
    if center_name_key not in name_map:
        return None, f"Person '{center_person_name}' not found."
    
    actual_center_name = name_map[center_name_key]
    
    # Build person lookup map
    person_map = {p['name'].lower(): p for p in full_data if 'name' in p}
    
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
                    
        return relevant_nodes, actual_center_name, G, spouses_map, person_map
    except Exception as e:
        return None, str(e)


def render_focused_tree(data, center_name):
    result = get_focused_subgraph(data, center_name)
    if not result or len(result) != 5:
        return None
        
    relevant_nodes, center_node, G, spouses_map, person_map = result

    # --- GRAPHVIZ SETUP ---
    dot = graphviz.Digraph(comment='Family Tree')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.6', ranksep='0.8')
    dot.attr('node', shape='plain', fontname='Sans-Serif') 

    # --- HELPER: GET GENDER ---
    def get_gender(name):
        p = person_map.get(name.lower().strip(), {})
        return p.get('gender', 'M') 

    # --- HELPER: GET STYLE (Color & Tooltip) ---
    def get_node_style(name):
        person = person_map.get(name.lower().strip(), {})
        assoc = person.get('association', '')
        
        # 1. Center Node: Gold
        if name == center_node:
            return '#FFD700', f"{name} (Focus)"
            
        # 2. In-Laws: Lavender Blush (Different from standard blue)
        # Check if 'in-law' is in the association text (case-insensitive)
        if assoc and 'in-law' in str(assoc).lower():
            return '#FFF0F5', f"{name} ({assoc})"
            
        # 3. Direct/Blood: Alice Blue
        tooltip = f"{name} ({assoc})" if assoc else name
        return '#E6F3FF', tooltip

    # --- RENDER NODES ---
    processed_pairs = set()
    added_nodes = set()
    node_id_map = {}

    # A. COUPLES
    for p1, p2 in spouses_map.items():
        if p1 in relevant_nodes and p2 in relevant_nodes:
            pair_key = tuple(sorted((p1, p2)))
            
            if pair_key not in processed_pairs:
                g1 = get_gender(p1)
                g2 = get_gender(p2)
                
                # Logic: Husband on Top
                top_p, bottom_p = pair_key[0], pair_key[1]
                if g1 == 'M' and g2 != 'M':
                    top_p, bottom_p = p1, p2
                elif g2 == 'M' and g1 != 'M':
                    top_p, bottom_p = p2, p1
                
                # Get Styles for each person in the couple
                bg_top, tip_top = get_node_style(top_p)
                bg_btm, tip_btm = get_node_style(bottom_p)

                # HTML Table Label with ALIGN="CENTER" and TOOLTIP
                label = f"""<
                <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" ROUNDED="TRUE">
                  <TR><TD ALIGN="CENTER" VALIGN="MIDDLE" BGCOLOR="{bg_top}" PORT="top" TOOLTIP="{tip_top}">{top_p}</TD></TR>
                  <TR><TD ALIGN="CENTER" VALIGN="MIDDLE" BGCOLOR="{bg_btm}" PORT="bottom" TOOLTIP="{tip_btm}">{bottom_p}</TD></TR>
                </TABLE>>"""
                
                node_id = f"{pair_key[0]}_{pair_key[1]}"
                dot.node(node_id, label=label)
                
                added_nodes.add(p1)
                added_nodes.add(p2)
                processed_pairs.add(pair_key)
                node_id_map[p1] = node_id
                node_id_map[p2] = node_id

    # B. SINGLES
    for node in relevant_nodes:
        if node not in added_nodes:
            bg_color, tooltip = get_node_style(node)
            
            label = f"""<
            <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" ROUNDED="TRUE">
              <TR><TD ALIGN="CENTER" VALIGN="MIDDLE" BGCOLOR="{bg_color}" PORT="center" TOOLTIP="{tooltip}">{node}</TD></TR>
            </TABLE>>"""
            
            node_id = node.replace(" ", "_")
            dot.node(node_id, label=label)
            
            added_nodes.add(node)
            node_id_map[node] = node_id

    # --- EDGES ---
    added_edges = set()
    for child in relevant_nodes:
        if child not in G: continue
        parents = list(G.predecessors(child))
        if not parents: continue
        
        father = next((p for p in parents if get_gender(p) == 'M'), parents[0])
        
        u = node_id_map.get(father)
        v = node_id_map.get(child)
        
        if u and v and u != v:
            if (u, v) not in added_edges:
                dot.edge(u, v, color='#555555')
                added_edges.add((u, v))

    return dot
