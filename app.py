import streamlit as st
from data.database import FAMILY_COLLECTION
import pandas as pd

from data.add_member import render_add_member_form
from data.edit_member import render_edit_member_form
from data.search_member import render_search_interface
from data.db_view import render_database_view

from handlers.graph_handlers import render_graph
from handlers.request_handlers import get_relatives

st.title("🔍 Bahlolpur Ancestry Database")

tab_view, tab_add, tab_edit, tab_data = st.tabs([
    "🔍 Search Tree",
    "➕ Add Member",
    "✏️ Edit Details",
    "📋 Database View"
])

with tab_view:
    render_search_interface(get_relatives, render_graph)

with tab_add:
    render_add_member_form(FAMILY_COLLECTION)

with tab_edit:
    render_edit_member_form(FAMILY_COLLECTION)

with tab_data:
    render_database_view(FAMILY_COLLECTION)