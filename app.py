import streamlit as st

st.set_page_config(page_title="बहलोलपुर वंशावली")

from data.database import FAMILY_COLLECTION, USERS_COLLECTION, EVENTS_COLLECTION
import pandas as pd

from data.add_member import render_add_member_form
from data.edit_member import render_edit_member_form
from data.view_details import render_search_interface
from data.events import render_events_page, render_add_event_form
from data.history_page import render_history_markdown
from data.db_view import render_database_view
from data.view_tree import render_tree_view
from data.lineage_info import render_lineage_sidebar
from handlers.request_handlers import get_relatives
from handlers.auth_handlers import handle_login, handle_logout

# 2. Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'nav_mode' not in st.session_state:
    st.session_state['nav_mode'] = "search"

if st.session_state.get('just_logged_in'):
    st.session_state['nav_mode'] = "admin"
    st.session_state['just_logged_in'] = False

render_lineage_sidebar()

st.title("🔍 बहलोलपुर वंशावली")

# 3. Navigation
selection = st.segmented_control(
    "Mode",
    options=["history", "search", "tree", "events", "admin"],
    format_func=lambda x: {
        "history": "ℹ️ history",
        "search": "🔍 Search",
        "tree": "🌳 Tree",
        "events": "📅 Events",
        "admin": "🔐 Admin Panel" if st.session_state['logged_in'] else "🔐 Admin"
    }[x],
    selection_mode="single",
    default=st.session_state['nav_mode'],
    key="nav_selection",
    on_change=lambda: st.session_state.update(nav_mode=st.session_state.nav_selection)
)

st.divider()

# --- PUBLIC SECTIONS ---
if selection == "history":
    render_history_markdown()

elif selection == "search":
    render_search_interface(get_relatives)

elif selection == "tree":
    render_tree_view(FAMILY_COLLECTION, None)

elif selection == "events":
    render_events_page(EVENTS_COLLECTION)

# --- ADMIN SECTION ---
elif selection == "admin":
    if not st.session_state['logged_in']:
        handle_login(USERS_COLLECTION)
    else:
        c1, c2 = st.columns([6, 1])
        with c1:
            st.info(f"👋 Welcome, **{st.session_state.get('user_name').title()}**")
        with c2:
            if st.button("Logout", type="secondary"):
                handle_logout()

        admin_tab = st.radio(
            "Manage Database:",
            options=["Add New Member", "Edit Details", "Add Event", "View Full Data"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown("---")

        if admin_tab == "Add New Member":
            render_add_member_form(FAMILY_COLLECTION)

        elif admin_tab == "Edit Details":
            render_edit_member_form(FAMILY_COLLECTION)

        elif admin_tab == "View Full Data":
            st.subheader("Full Database Registry")
            render_database_view(FAMILY_COLLECTION)

        elif admin_tab == "Add Event":
            render_add_event_form()
