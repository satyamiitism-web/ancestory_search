import streamlit as st
from handlers.graph_handlers import render_focused_tree

def render_tree_view(collection, _): 
    st.header("🌳 View Family Tree")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input(
                "Search Family Member",
                placeholder="Enter full name (e.g., Satyam Anand)",
                label_visibility="collapsed"
            )
    with col2:
        search_btn = st.button("Generate Tree", type="primary")

    if search_btn and search_name:
        all_members = list(collection.find({}, {"_id": 0}))
        
        with st.spinner(f"Tracing lineage for {search_name}..."):
            # This now returns a Graphviz object
            graph = render_focused_tree(all_members, search_name)
            
            if graph:
                # Streamlit has a native graphviz renderer!
                st.graphviz_chart(graph, use_container_width=True)
            
    elif search_btn:
        st.warning("Please enter a name first.")
