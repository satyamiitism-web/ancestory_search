import asyncio

import streamlit as st

from data.lineage_info import render_lineage_sidebar
from handlers.ui_handlers import (configure_page, init_session_state,
                                  render_navigation, route_request)


async def main():
    await configure_page()
    await init_session_state()
    
    # Sidebar Info
    await render_lineage_sidebar()

    st.title("🔍 बहलोलपुर वंशावली")

    # Render Nav and get selection
    selection = await render_navigation()
    
    st.divider()
    
    # Route to content
    await route_request(selection)

if __name__ == "__main__":
    asyncio.run(main())
