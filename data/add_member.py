import streamlit as st
import random
import time
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

def render_add_member_form(collection):
    """
    Renders the form to add a new family member.
    Handles duplicate names by creating unique IDs using an incremental counter logic.
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

        association = st.selectbox("Association", ["son", "daughter", "son-in-law", "daughter-in-law"])

        # Row 2: Parents
        st.markdown("### Parents")
        p1, p2 = st.columns(2)
        with p1:
            father = st.text_input("Father's Name", placeholder="e.g. Madhukar Anand")
        with p2:
            mother = st.text_input("Mother's Name", placeholder="e.g. Nilu Sharma")

        # Row 3: Parent-in-laws
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

        # 1. Clean Inputs
        clean_name = name.strip()
        clean_father = father.strip()
        clean_spouse = spouse.strip()
        
        parents = [p.strip() for p in [father, mother] if p.strip()]
        parents_in_law = [p.strip() for p in [father_in_law, mother_in_law] if p.strip()]

        base_str = clean_name.lower().replace(" ", "-")

        final_slug = base_str
        counter = 1

        # Loop until we find a slug that DOES NOT exist
        while collection.find_one({"slug": final_slug}):
            final_slug = f"{base_str}-{counter}"
            counter += 1

        # 4. Prepare Document
        current_timestamp = datetime.now(timezone.utc)
        current_user = st.session_state.get("user_name", "Admin").title()

        new_doc = {
            "slug": final_slug,  # <--- Guaranteed Unique
            "name": clean_name,
            "gender": gender,
            "spouse": clean_spouse,
            "parents": parents,
            "parents_in_law": parents_in_law,
            "phone": phone.strip(),
            "work": work.strip(),
            "association": association.strip(),
            "created_at": current_timestamp,
            "updated_at": current_timestamp,
            "updated_by": current_user
        }

        # 5. Insert
        try:
            collection.insert_one(new_doc)
            st.success(f"✅ **{clean_name}** added successfully!")
            st.caption(f"Unique ID generated: `{final_slug}`") 
            
        except DuplicateKeyError:
            # Should be impossible due to the while loop check
            st.error(f"⚠️ A record for **{clean_name}** already exists (ID Collision).")
        except Exception as e:
            st.error(f"❌ Database Error: {e}")