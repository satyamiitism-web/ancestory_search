import streamlit as st
from handlers.graph_handlers import render_focused_tree

def render_tree_view(collection, _): 
    st.header("🌳 View Family Tree")

    # --- 1. Fetch Data & Build Labels (Same logic as Search Tab) ---
    raw_members = list(collection.find({}, {
        "name": 1, 
        "association": 1,
        "parents": 1, 
        "spouse": 1,
        "gender": 1,
        "_id": 0
    }).sort("name", 1))

    name_map = {}
    display_options = []

    for m in raw_members:
        name = m.get('name', 'Unknown')
        assoc = str(m.get('association', '')).lower().strip()
        
        def get_first(field):
            val = m.get(field)
            if isinstance(val, list) and val: return val[0]
            if isinstance(val, str): return val
            return None

        spouse_name = get_first('spouse')
        father_name = get_first('parents')
        
        relation_suffix = ""

        # LOGIC: Association-based context
        if "daughter-in-law" in assoc or "bahu" in assoc:
            if spouse_name: relation_suffix = f"(w/o {spouse_name})"
            elif father_name: relation_suffix = f"(d/o-in-law of {father_name})"

        elif "son-in-law" in assoc or "damad" in assoc:
            if father_name: relation_suffix = f"(s/o-in-law of {father_name})"
            elif spouse_name: relation_suffix = f"(h/o {spouse_name})"

        else: # Son/Daughter/Default
            if father_name:
                # Decide s/o vs d/o
                is_female = "daughter" in assoc or "female" in str(m.get('gender','')).lower()
                prefix = "d/o" if is_female else "s/o"
                relation_suffix = f"({prefix} {father_name})"
            elif spouse_name:
                 is_female = "female" in str(m.get('gender','')).lower()
                 prefix = "w/o" if is_female else "h/o"
                 relation_suffix = f"({prefix} {spouse_name})"

        full_label = f"{name} {relation_suffix}".strip()
        display_options.append(full_label)
        name_map[full_label] = name

    # --- 2. Render Search Widget ---
    # We remove the columns/button layout and use the cleaner multiselect approach
    
    selected_label_list = st.multiselect(
        "Search Family Member to Generate Tree",
        options=display_options,
        placeholder="Type name to generate tree...",
        max_selections=1,
        label_visibility="collapsed"
    )

    # --- 3. Handle Selection & Generate Graph ---
    if selected_label_list:
        label_selected = selected_label_list[0]
        real_name = name_map[label_selected]
        
        # We need the full list for the recursive graph logic
        # (Already fetched in 'raw_members' but graph handler might need clean dicts)
        # Re-using raw_members is fine if render_focused_tree expects list of dicts.
        
        with st.spinner(f"Tracing lineage for {real_name}..."):
            # Note: raw_members only has partial fields (projection). 
            # If render_focused_tree needs ALL fields, fetch full collection again:
            full_data_for_graph = list(collection.find({}, {"_id": 0}))
            
            graph = render_focused_tree(full_data_for_graph, real_name)
            
            if graph:
                st.graphviz_chart(graph, use_container_width=True)
            else:
                st.warning(f"Could not generate tree for {real_name}.")
