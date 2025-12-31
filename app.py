import streamlit as st

# 1. Page Config
st.set_page_config(page_title="बहलोलपुर वंशावली")

from data.database import FAMILY_COLLECTION, USERS_COLLECTION
import pandas as pd

from data.add_member import render_add_member_form
from data.edit_member import render_edit_member_form
from data.view_details import render_search_interface
from data.db_view import render_database_view
from data.view_tree import render_tree_view
from handlers.request_handlers import get_relatives
# Import new Auth Handlers
from handlers.auth_handlers import handle_login, handle_logout

# 2. Initialize Session State
# 2. Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Initialize the navigation mode if not present
if 'nav_mode' not in st.session_state:
    st.session_state['nav_mode'] = "search"

# If user just logged in (detected via flag or logic), force mode to admin
if st.session_state.get('just_logged_in'):
    st.session_state['nav_mode'] = "admin"
    st.session_state['just_logged_in'] = False # Reset flag

st.title("🔍 बहलोलपुर वंशावली")

# 3. Navigation
selection = st.segmented_control(
    "Mode",
    options=["search", "tree", "admin"],
    format_func=lambda x: {
        "search": "🔍 Search Member",
        "tree": "🌳 View Full Tree",
        "admin": "🔐 Admin Panel" if st.session_state['logged_in'] else "🔐 Admin Login"
    }[x],
    selection_mode="single",
    default=st.session_state['nav_mode'], # Use session state variable
    key="nav_selection", # <--- CRITICAL: Keeps widget in sync
    on_change=lambda: st.session_state.update(nav_mode=st.session_state.nav_selection) # Update state on click
)

st.divider()

# --- PUBLIC SECTIONS ---
if selection == "search":
    render_search_interface(get_relatives)

elif selection == "tree":
    render_tree_view(FAMILY_COLLECTION, None)

# --- ADMIN SECTION ---
elif selection == "admin":
    
    # CASE A: User NOT Logged In -> Show Login Form
    if not st.session_state['logged_in']:
        handle_login(USERS_COLLECTION)

    # CASE B: User IS Logged In -> Show Admin Panel
    else:
        # Header with User Info & Logout
        c1, c2 = st.columns([6, 1])
        with c1:
            st.info(f"👋 Welcome, **{st.session_state.get('user_name').title()}**")
        with c2:
            if st.button("Logout", type="secondary"):
                handle_logout()

        # Internal Admin Tabs
        admin_tab = st.radio(
            "Manage Database:",
            options=["Add New Member", "Edit Details", "View Full Data"],
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