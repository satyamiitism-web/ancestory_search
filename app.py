import streamlit as st

st.set_page_config(page_title="बहलोलपुर वंशावली")

import pandas as pd
from streamlit_option_menu import option_menu

from data.add_member import render_add_member_form
from data.bulk_update import render_bulk_update_form
from data.database import (EVENTS_COLLECTION, FAMILY_COLLECTION,
                           USERS_COLLECTION)
from data.db_view import render_database_view
from data.edit_member import render_edit_member_form
from data.events import render_add_event_form, render_events_page
from data.history_page import render_history_markdown
from data.lineage_info import render_lineage_sidebar
from data.view_details import render_search_interface
from data.view_tree import render_tree_view
from handlers.auth_handlers import handle_login, handle_logout
from handlers.request_handlers import get_relatives

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

nav_config = {
    "history": {"label": "History", "icon": "info-circle"},
    "search": {"label": "Search", "icon": "search"},
    "tree": {"label": "Tree", "icon": "diagram-3"},
    "events": {"label": "Events", "icon": "calendar-event"},
    "admin": {
        "label": "Admin Panel" if st.session_state.get('logged_in') else "Admin", 
        "icon": "lock"
    },
}

options_list = [val["label"] for val in nav_config.values()]
icons_list = [val["icon"] for val in nav_config.values()]
keys_list = list(nav_config.keys())

current_mode = st.session_state.get('nav_mode', 'search')
try:
    default_index = keys_list.index(current_mode)
except ValueError:
    default_index = 1

selected_label = option_menu(
    menu_title=None,
    options=options_list,
    icons=icons_list,
    default_index=default_index,
    orientation="horizontal",
    styles={
        # Remove hardcoded background so it fits dark mode
        "container": {
            "padding": "0!important", 
            "background-color": "transparent"
        },
        # Icon color (orange works well on both, or remove to use default)
        "icon": {
            "color": "orange", 
            "font-size": "18px"
        }, 
        # Text color: removing 'color' lets it adapt to the theme (white in dark mode, black in light)
        "nav-link": {
            "font-size": "16px", 
            "text-align": "center", 
            "margin": "0px", 
            "--hover-color": "#262730",  # Slight dark grey for hover in dark mode
        },
        # Selected background: Streamlit's primary red looks good on both
        "nav-link-selected": {
            "background-color": "#ff4b4b"
        },
    }
)
selection = next(key for key, val in nav_config.items() if val["label"] == selected_label)

if st.session_state.get('nav_mode') != selection:
    st.session_state['nav_mode'] = selection
    st.rerun()

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
            options=["Add New Member", "Edit Details", "Add Event", "Bulk Update", "View Full Data"],
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

        elif admin_tab == "Bulk Update":
            render_bulk_update_form()
