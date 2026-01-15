import streamlit as st


async def render_lineage_sidebar():
    with st.sidebar.expander("📜 वंश परिचय", expanded=True):
        st.markdown("""
        **📍 स्थान:** उत्तर प्रदेश (सीतापुर से 36 किमी)
        
        ---
        **🏡 उद्गम:** ग्राम नैमिषारण्य (पूर्वजों की उत्पत्ति)

        ---
        **मूल:** एकसार\n
        **वंश:** एकसरिया\n
        **गोत्र:** पराशर मुनि\n

        **🔥 परवर:**
        1. वशिष्ठ
        2. शक्ति
        3. पराशर
        """)