import streamlit as st
from streamlit_option_menu import option_menu

from data.database import EVENTS_COLLECTION, FAMILY_COLLECTION
from data.events import render_events_page
from data.history_page import render_history_markdown
from data.view_details import render_search_interface
from data.view_tree import render_tree_view

from .admin_handlers import handle_admin_section
from .request_handlers import get_relatives


async def configure_page():
    st.set_page_config(page_title="बहलोलपुर वंशावली")

async def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'logged_in': False,
        'nav_mode': "search",
        'just_logged_in': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Handle post-login redirection logic
    if st.session_state['just_logged_in']:
        st.session_state['nav_mode'] = "admin"
        st.session_state['just_logged_in'] = False


async def render_navigation():
    """Renders the top navigation bar and returns the selected page."""
    
    # Dynamic config based on login state
    admin_label = "Admin Panel" if st.session_state.get('logged_in') else "Admin"
    
    nav_config = {
        "history": {"label": "History", "icon": "info-circle"},
        "search": {"label": "Search", "icon": "search"},
        "tree":   {"label": "Tree", "icon": "diagram-3"},
        "events": {"label": "Events", "icon": "calendar-event"},
        "admin":  {"label": admin_label, "icon": "lock"},
    }

    options_list = [val["label"] for val in nav_config.values()]
    icons_list = [val["icon"] for val in nav_config.values()]
    keys_list = list(nav_config.keys())

    # Determine default index based on current state
    current_mode = st.session_state.get('nav_mode', 'search')
    try:
        default_index = keys_list.index(current_mode)
    except ValueError:
        default_index = 1  # Default to Search if mode is invalid

    selected_label = option_menu(
        menu_title=None,
        options=options_list,
        icons=icons_list,
        default_index=default_index,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "16px", "text-align": "center", "margin": "0px", 
                "--hover-color": "#262730"
            },
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )

    # Convert label back to internal key
    selection = next(key for key, val in nav_config.items() if val["label"] == selected_label)

    # Handle state updates and reruns
    if st.session_state.get('nav_mode') != selection:
        st.session_state['nav_mode'] = selection
        st.rerun()
        
    return selection

async def route_request(selection):
    """Routes the main navigation selection to the appropriate renderer."""
    if selection == "history":
        await render_history_markdown() 
    
    elif selection == "search":
        await render_search_interface(get_relatives)
    
    elif selection == "tree":
        await render_tree_view(FAMILY_COLLECTION, None)
    
    elif selection == "events":
        await render_events_page(EVENTS_COLLECTION)
    
    elif selection == "admin":
        await handle_admin_section()

