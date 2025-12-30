import streamlit as st
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone  # <--- IMPORT ADDED


def render_add_member_form(collection):
    """
    Renders the form to add a new family member.
    """
    st.header("📝 Add New Member")
    
    with st.form("add_member_form", clear_on_submit=True):
        # Row 1: Basic Info
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            name = st.text_input("Full Name", placeholder="e.g. Satyam Anand")
        with c2:
            spouse = st.text_input("Spouse Name", placeholder="e.g. Golden (Optional)")
        with c3:
            gender = st.selectbox("Gender", ["M", "F", "Other"])

        # Row 2: Parents
        st.markdown("### Parents")
        p1, p2 = st.columns(2)
        with p1:
            father = st.text_input("Father's Name", placeholder="e.g. Madhukar Anand")
        with p2:
            mother = st.text_input("Mother's Name", placeholder="e.g. Nilu Sharma")

        # Row 3: Parent-in-laws (Always Visible)
        st.markdown("### Parent-in-laws")
        pil1, pil2 = st.columns(2)
        with pil1:
            father_in_law = st.text_input("Father-in-law's Name")
        with pil2:
            mother_in_law = st.text_input("Mother-in-law's Name")

        # Row 4: Contact & Work
        st.markdown("### Contact & Work")
        w1, w2 = st.columns(2)
        with w1:
            phone = st.text_input("Phone Number", placeholder="e.g. +91 9876543210")
        with w2:
            work = st.text_input("Work Details", placeholder="e.g. Software Engineer")

        submitted = st.form_submit_button("💾 Save to Database", use_container_width=True)

    # --- Handle Submission ---
    if submitted:
        if not name:
            st.error("❌ Name is mandatory!")
            return

        # Prepare Data
        slug = name.lower().strip()
        parents = [p.strip() for p in [father, mother] if p.strip()]
        parents_in_law = [p.strip() for p in [father_in_law, mother_in_law] if p.strip()]

        # --- NEW: Get Current Timestamp (UTC) ---
        current_timestamp = datetime.now(timezone.utc)

        new_doc = {
            "slug": slug,
            "name": name.strip(),
            "gender": gender,
            "spouse": spouse.strip(),
            "parents": parents,
            "parents_in_law": parents_in_law, 
            "phone": phone.strip(),
            "work": work.strip(),
            # --- NEW: Add Timestamps ---
            "created_at": current_timestamp,
            "updated_at": current_timestamp
        }

        # Insert into MongoDB
        try:
            collection.insert_one(new_doc)
            st.success(f"✅ **{name}** added successfully!")
            
        except DuplicateKeyError:
            st.error(f"⚠️ **{name}** already exists in the family tree.")
        except Exception as e:
            st.error(f"❌ Database Error: {e}")
