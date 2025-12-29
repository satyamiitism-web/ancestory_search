import streamlit as st

def render_search_interface(get_relatives_func, render_graph_func):
    """
    Renders the family tree search interface.
    
    Args:
        get_relatives_func: Function to fetch family data (returns dict or None)
        render_graph_func: Function to generate Graphviz source
    """
    st.header("🌳 Family Tree Explorer")
    st.caption("Discover relationships, ancestors, and descendants.")

    # --- 1. Search Bar ---
    # Using a container to group the input cleanly
    with st.container():
        c1, c2 = st.columns([4, 1])
        with c1:
            name_input = st.text_input(
                "Search Family Member", 
                placeholder="Enter full name (e.g., Satyam Anand)",
                label_visibility="collapsed"
            )
        with c2:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

    # --- 2. Result Handling ---
    if search_clicked:
        if not name_input.strip():
            st.toast("⚠️ Please enter a name to search.")
            return

        with st.spinner(f"Searching for '{name_input}'..."):
            results = get_relatives_func(name_input)

        if results:
            _display_family_results(results, render_graph_func)
        else:
            st.error(f"❌ **{name_input}** was not found in the records.")
            st.info("💡 Tip: Try checking the spelling or adding them in the 'Add Member' tab.")

def _display_family_results(results, render_graph_func):
    """Internal helper to display the results nicely."""
    
    target = results['target']
    
    # --- Header Section ---
    st.divider()
    st.subheader(f"👤 {target['name']}")
    st.caption(f"Gender: {target.get('gender', 'N/A')}")

    # --- Data Preparation ---
    # Helper to format lists safely
    def format_list(person_list):
        if not person_list:
            return "—"
        return ", ".join([f"**{p['name']}**" for p in person_list])

    spouse_val = f"**{results['spouse']['name']}**" if results['spouse'] else "—"
    children_val = format_list(results['children'])
    parents_val = format_list(results['parents'])
    grandparents_val = format_list(results['grandparents'])

    # --- Visual Cards Layout (Better than a table) ---
    # This grid layout is more modern than a markdown table
    c1, c2 = st.columns(2)
    
    with c1:
        st.info(f"❤️ **Spouse**\n\n{spouse_val}")
        st.warning(f"👪 **Parents**\n\n{parents_val}")
        
        
    with c2:
        st.success(f"👶 **Children**\n\n{children_val}")
        st.error(f"👴👵 **Grandparents**\n\n{grandparents_val}")

    # --- Visualization Section ---
    # st.divider()
    # if st.button("🕸️ See Family Tree", type="primary", use_container_width=True):
    # st.subheader(f"Lineage: {target['name']}")

    # Render the graph
    # try:
        # graph_source = render_graph_func(results)
        # st.graphviz_chart(graph_source, use_container_width=True)
    # except Exception as e:
        # st.warning(f"Could not generate graph: {e}")

