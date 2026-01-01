import streamlit as st
import time
from pymongo.errors import PyMongoError
from datetime import datetime, timezone

def render_edit_member_form(collection):
    """
    Renders the Edit/Manage Member interface.
    Includes Association field and Timestamps.
    """
    
    # --- 1. AUTO-RESET LOGIC ---
    c_head, c_reset = st.columns([4, 1])
    with c_head:
        st.header("👤 Manage Member Details")
    with c_reset:
        if st.button("🔄 Reset", type="tertiary", help="Clear current selection"):
            if 'current_person' in st.session_state:
                del st.session_state['current_person']
            st.session_state['is_editing'] = False
            st.rerun()

    # --- 2. SEARCH SECTION ---
    with st.container():
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input(
                "Find Person", 
                placeholder="Enter name to edit/delete...", 
                label_visibility="collapsed",
                key="edit_search_box"
            )
        with search_col2:
            search_btn = st.button("🔍 Search", use_container_width=True, key="edit_search_btn")

    if search_btn:
        if not search_query:
            st.toast("⚠️ Please enter a name first.")
        else:
            slug = search_query.lower().strip()
            person = collection.find_one({"slug": slug})

            if person:
                st.session_state['current_person'] = person
                st.session_state['is_editing'] = False
                st.toast(f"✅ Found {person['name']}")
            else:
                st.error(f"❌ Could not find anyone named '{search_query}'")
                if 'current_person' in st.session_state:
                    del st.session_state['current_person']

    # --- 3. DISPLAY / EDIT SECTION ---
    if 'current_person' in st.session_state:
        person = st.session_state['current_person']
        st.divider()

        # CHECK: Are we in Edit Mode?
        if not st.session_state.get('is_editing', False):
            # --- VIEW MODE (Read Only) ---
            st.subheader(f"📄 {person['name']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Gender:** {person.get('gender', 'N/A')}")
                st.markdown(f"**Spouse:** {person.get('spouse', 'None')}")
                st.markdown(f"**Phone:** {person.get('phone', '—')}")
                # NEW: Show Association
                st.markdown(f"**Association:** {person.get('association', '—')}")
                
            with col_b:
                parents = person.get('parents', [])
                parents_str = ", ".join(parents) if parents else "Unknown"
                st.markdown(f"**Parents:** {parents_str}")
                st.markdown(f"**Work:** {person.get('work', '—')}")

            # View Parent-in-laws if they exist
            in_laws = person.get('parents_in_law', [])
            if in_laws:
                st.markdown("---")
                st.markdown(f"**Parents-in-Law:** {', '.join(in_laws)}")

            st.divider()
            
            # Action Buttons Row
            action_col1, action_col2, action_col3 = st.columns([2, 2, 4])
            
            with action_col1:
                if st.button("✏️ Edit Details", use_container_width=True):
                    st.session_state['is_editing'] = True
                    st.rerun()
            
            with action_col2:
                # DELETE BUTTON
                if st.button("🗑️ Delete", type="primary", use_container_width=True):
                    st.session_state['confirm_delete'] = True
                    st.rerun()

            # --- DELETE CONFIRMATION DIALOG ---
            if st.session_state.get('confirm_delete', False):
                st.warning(f"⚠️ Are you sure you want to permanently delete **{person['name']}**?")
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                        try:
                            collection.delete_one({"_id": person['_id']})
                            st.success(f"🗑️ Deleted **{person['name']}**")
                            # Cleanup State
                            del st.session_state['current_person']
                            del st.session_state['confirm_delete']
                            time.sleep(1.5)
                            st.rerun()
                        except PyMongoError as e:
                            st.error(f"Delete Failed: {e}")
                with d_col2:
                    if st.button("❌ No, Cancel", use_container_width=True):
                        st.session_state['confirm_delete'] = False
                        st.rerun()

        else:
            # --- EDIT MODE (Form) ---
            st.subheader(f"✏️ Editing: {person['name']}")
            
            with st.form("update_form"):
                # Basic Info
                new_name = st.text_input("Full Name", value=person['name'])
                
                c1, c2 = st.columns(2)
                with c1:
                    g_opts = ["M", "F", "Other"]
                    curr_g = person.get('gender', 'M')
                    idx = g_opts.index(curr_g) if curr_g in g_opts else 0
                    new_gender = st.selectbox("Gender", g_opts, index=idx)
                with c2:
                    new_spouse = st.text_input("Spouse Name", value=person.get('spouse', ''))

                # Parents
                st.markdown("### Parents")
                curr_parents = person.get('parents', [])
                p1_val = curr_parents[0] if len(curr_parents) > 0 else ""
                p2_val = curr_parents[1] if len(curr_parents) > 1 else ""
                
                pc1, pc2 = st.columns(2)
                with pc1:
                    new_father = st.text_input("Father", value=p1_val)
                with pc2:
                    new_mother = st.text_input("Mother", value=p2_val)

                # Parent-in-laws
                st.markdown("### Parent-in-laws")
                curr_in_laws = person.get('parents_in_law', [])
                pil1_val = curr_in_laws[0] if len(curr_in_laws) > 0 else ""
                pil2_val = curr_in_laws[1] if len(curr_in_laws) > 1 else ""

                pil_c1, pil_c2 = st.columns(2)
                with pil_c1:
                    new_father_in_law = st.text_input("Father-in-law", value=pil1_val)
                with pil_c2:
                    new_mother_in_law = st.text_input("Mother-in-law", value=pil2_val)

                # --- NEW: ASSOCIATION FIELD ---
                st.markdown("### Relationship & Work")
                
                # Pre-define common family associations for consistent data
                assoc_options = ["son", "daughter", "daughter-in-law", "son-in-law"]
                
                # Get current value
                curr_assoc = person.get('association', 'son')
                
                # Find index or default to 0 (Son)
                # We do a loose match or exact match
                assoc_idx = 0
                if curr_assoc in assoc_options:
                    assoc_idx = assoc_options.index(curr_assoc)
                else:
                    # If existing value is not in our list, append it temporarily so it shows up
                    assoc_options.append(curr_assoc)
                    assoc_idx = len(assoc_options) - 1

                w1, w2 = st.columns(2)
                with w1:
                    new_association = st.selectbox("Association (Relation Type)", options=assoc_options, index=assoc_idx)
                with w2:
                    new_phone = st.text_input("Phone Number", value=person.get('phone', ''))
                
                # Work Details
                new_work = st.text_input("Work Details", value=person.get('work', ''))

                st.divider()
                
                # Footer Buttons
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    submit_update = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with btn_col2:
                    cancel_edit = st.form_submit_button("❌ Cancel Edit", type="secondary", use_container_width=True)

            # --- Handle Form Logic ---
            if cancel_edit:
                st.session_state['is_editing'] = False
                st.rerun()

            if submit_update:
                try:
                    # Prepare Data
                    updated_parents = [p.strip() for p in [new_father, new_mother] if p.strip()]
                    updated_in_laws = [p.strip() for p in [new_father_in_law, new_mother_in_law] if p.strip()]

                    current_timestamp = datetime.now(timezone.utc)
                    current_user = st.session_state.get("user_name", "Admin").title()

                    update_payload = {
                        "slug": new_name.lower().strip(),
                        "name": new_name.strip(),
                        "gender": new_gender,
                        "spouse": new_spouse.strip(),
                        "parents": updated_parents,
                        "parents_in_law": updated_in_laws, 
                        "phone": new_phone.strip(),
                        "work": new_work.strip(),
                        "association": new_association, # <--- NEW FIELD IN PAYLOAD
                        "updated_at": current_timestamp,
                        "updated_by": current_user
                    }

                    # DB Update
                    collection.update_one({"_id": person['_id']}, {"$set": update_payload})
                    
                    # Update local state
                    st.session_state['current_person'].update(update_payload)
                    st.session_state['is_editing'] = False 
                    
                    st.success("✅ Details updated successfully!")
                    time.sleep(1) 
                    st.rerun()
                    
                except PyMongoError as e:
                    st.error(f"Update failed: {e}")
