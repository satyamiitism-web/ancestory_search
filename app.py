import streamlit as st

from handlers.graph_handlers import render_graph
from handlers.request_handlers import get_relatives

st.title("🔍 Bahlolpur Ancestry Database")

with st.form(key='search_form'):
    name_input = st.text_input("Enter Name", placeholder="e.g. Satyam Anand")
    submit_button = st.form_submit_button(label='Search')

# 2. Trigger logic when button is clicked OR name is provided
if submit_button and name_input:
    results = get_relatives(name_input)

    if results:
        # ... (Same string preparation logic as above) ...
        spouse_str = results['spouse']['name'] if results['spouse'] else "None"
        children_str = ", ".join([c['name'] for c in results['children']]) or "None"
        parents_str = ", ".join([p['name'] for p in results['parents']]) or "None"
        grandparents_str = ", ".join([gp['name'] for gp in results['grandparents']]) or "None"

        # Create a markdown table manually
        markdown_table = f"""
        | Relationship | Names |
        | :--- | :--- |
        | **❤️ Spouse** | {spouse_str} |
        | **👶 Children** | {children_str} |
        | **👪 Parents** | {parents_str} |
        | **👴👵 Grandparents** | {grandparents_str} |
        """

        st.markdown("### Family Details")
        st.markdown(markdown_table)
        st.markdown("---")
            # --- Display Graph ---
        st.subheader("Visualization")
        st.graphviz_chart(render_graph(results))

    else:
        st.error("Person not found in database.")
elif submit_button and not name_input:
    st.warning("Please enter a name first.")
