import streamlit as st

def render_search_interface(get_relatives_func, render_graph_func):
    """
    Renders the family tree search interface.
    """
    st.header("🌳 Family Tree Explorer")
    st.caption("Discover relationships, ancestors, and descendants.")

    # --- 1. Search Bar ---
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
    
    # --- Data Extraction ---
    phone = target.get('phone', '—')
    work = target.get('work', '—')
    gender = target.get('gender', 'N/A')
    
    # Extract Parent-in-laws
    parents_in_law_list = target.get('parents_in_law', [])

    # --- Header Section ---
    st.divider()
    st.subheader(f"👤 {target['name']}")
    
    # Metadata Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.caption(f"**Gender:** {gender}")
    with m2:
        st.markdown(f"📞 **Phone:** {phone}")
    with m3:
        st.markdown(f"💼 **Work:** {work}")

    # --- Relationship Data Preparation ---
    def format_list(person_list):
        if not person_list:
            return "—"
        # Check if list contains objects (like children/parents results) or just strings
        if isinstance(person_list[0], dict) and 'name' in person_list[0]:
             return ", ".join([f"**{p['name']}**" for p in person_list])
        return ", ".join([f"**{p}**" for p in person_list])

    spouse_val = f"**{results['spouse']['name']}**" if results['spouse'] else "—"
    children_val = format_list(results['children'])
    parents_val = format_list(results['parents'])
    grandparents_val = format_list(results['grandparents'])
    
    # Format In-Laws string
    in_laws_val = format_list(parents_in_law_list) if parents_in_law_list else "—"

    # --- Visual Cards Layout ---
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"❤️ **Spouse**\n\n{spouse_val}")
        st.warning(f"👪 **Parents**\n\n{parents_val}")
        
    with c2:
        st.success(f"👶 **Children**\n\n{children_val}")
        st.error(f"👴👵 **Grandparents**\n\n{grandparents_val}")

    # --- In-Laws Section ---
    # Display if data exists, regardless of gender
    if parents_in_law_list:
        st.info(f"🏘️ **Parents-in-Law**\n\n{in_laws_val}")

    # st.divider()
    # st.caption("Family Lineage Visualization")
    # try:
    #     graph_source = render_graph_func(results)
    #     st.graphviz_chart(graph_source, use_container_width=True)
    # except Exception as e:
    #     st.warning(f"Could not generate graph: {e}")
