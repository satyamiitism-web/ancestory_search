import streamlit as st


async def render_history_markdown():
    st.header("📜 हमारा इतिहास")
    st.markdown("---")

    # --- SECTION 1: MIGRATION JOURNEY (Timeline Style) ---
    st.subheader("🚶 पूर्वजों की यात्रा")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Visual Map/Icon representation
        st.markdown(
            """
            <div style="text-align: center; font-size: 3rem; line-height: 1.5;">
                🏰<br>⬇<br>🏡<br>⬇<br>📍
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        # Structured Timeline
        st.info("**1. उद्गम (Origin):**  \nपुरुषोत्तम दीक्षित का जन्म **नैमिषारण्य (सीतापुर, उत्तर प्रदेश)** में हुआ था।")
        
        st.warning("**2. प्रवास (Migration):**  \nउनके पुत्र **दया मिश्र** मूल स्थान छोड़कर **भेल्दी (छपरा, बिहार)** में बस गए।")
        
        st.success("**3. विस्तार (Settlement):**  \nदया मिश्र के दो पुत्रों ने अलग-अलग स्थान चुने:\n* **लोहा मिश्र:** जाफराबाद (वैशाली) चले गए।\n* **मोती मिश्र:** **बहलोलपुर** में बस गए (हम सब उन्हीं के वंशज हैं)।")

    st.markdown("---")

    # --- SECTION 2: LINEAGE BRANCHES (Card Layout) ---
    st.subheader("🌳 बहलोलपुर की पट्टियां")
    st.caption("मोती मिश्र की तीन संतानों से बहलोलपुर में ये पट्टियां बनीं:")

    # Create 3 columns for the 3 main branches
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.markdown("### 1️⃣ महाराजी पट्टी")
            st.divider()
            st.markdown("**पूर्वज:** रामजी मिश्रा")

    with c2:
        with st.container(border=True):
            st.markdown("### 2️⃣ तीनपटिया")
            st.divider()
            st.markdown("**पूर्वज:** तहवल मिश्रा")
            st.markdown("- भूखा मिश्रा")

    with c3:
        with st.container(border=True):
            st.markdown("### 3️⃣ चारपटिया")
            st.divider()
            st.markdown("**पूर्वज:** तहवल मिश्रा")
            st.markdown("- हेमन मिश्रा")

    with c4:
        with st.container(border=True):
            st.markdown("### 4️⃣ पचपटिया")
            st.divider()
            st.markdown("**पूर्वज:** महादेव मिश्रा")

    # Optional: Summary Footer
    st.markdown("---")
    st.caption("📍 *यह जानकारी हमारे पूर्वजों और पारिवारिक अभिलेखों पर आधारित है।*")
