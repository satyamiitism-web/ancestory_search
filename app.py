import streamlit as st
from data.database import FAMILY_COLLECTION
import pandas as pd

from data.add_member import render_add_member_form
from data.edit_member import render_edit_member_form
from data.search_member import render_search_interface
from data.db_view import render_database_view

from handlers.graph_handlers import render_graph
from handlers.request_handlers import get_relatives

st.title("🔍 बहलोलपुर वंशावली")

selection = st.segmented_control(
    "Mode",
    options=["search", "add", "edit", "data"],
    format_func=lambda x: {
        "search": "🔍 Search Tree",
        "add": "➕ Add Member",
        "edit": "✏️ Edit Details",
        "data": "📋 Database View"
    }[x],
    selection_mode="single",
    default="search"
)

st.divider()

if selection == "search":
    render_search_interface(get_relatives, render_graph)

elif selection == "add":
    render_add_member_form(FAMILY_COLLECTION)

elif selection == "edit":
    render_edit_member_form(FAMILY_COLLECTION)

elif selection == "data":
    st.subheader("Full Database Registry")
    render_database_view(FAMILY_COLLECTION)