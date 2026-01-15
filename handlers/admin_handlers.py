import streamlit as st

from data.add_member import render_add_member_form
from data.bulk_update import render_bulk_update_form
from data.database import FAMILY_COLLECTION, USERS_COLLECTION
from data.db_view import render_database_view
from data.edit_member import render_edit_member_form
from data.events import render_add_event_form

from .auth_handlers import handle_login, handle_logout


async def render_admin_dashboard():
    """Handles the authenticated admin interface."""
    c1, c2 = st.columns([6, 1])
    with c1:
        st.info(f"👋 Welcome, **{st.session_state.get('user_name', '').title()}**")
    with c2:
        if st.button("Logout", type="secondary"):
            await handle_logout()

    user_role = st.session_state.get('user_role', 'maintainer')

    all_options = {
        "Add New Member": ["admin", "maintainer"],
        "Add Event":      ["admin", "maintainer"],
        "Edit Details":   ["admin"],
        "Bulk Update":    ["admin"],
        "View Full Data": ["admin"]
    }

    allowed_options = [opt for opt, roles in all_options.items() if user_role in roles]

    admin_tab = st.radio(
        "Manage Database:",
        options=allowed_options,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("---")

    # Dispatcher for Admin Tabs
    if admin_tab == "Add New Member":
        await render_add_member_form(FAMILY_COLLECTION)
    elif admin_tab == "Edit Details":
        await render_edit_member_form(FAMILY_COLLECTION)
    elif admin_tab == "View Full Data":
        st.subheader("Full Database Registry")
        await render_database_view(FAMILY_COLLECTION)
    elif admin_tab == "Add Event":
        await render_add_event_form()
    elif admin_tab == "Bulk Update":
        await render_bulk_update_form()

async def handle_admin_section():
    """Router for the Admin section (Login vs Dashboard)."""
    if not st.session_state['logged_in']:
        await handle_login(USERS_COLLECTION)
    else:
        await render_admin_dashboard()