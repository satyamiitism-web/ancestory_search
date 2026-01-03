import time
from datetime import datetime, timezone

import streamlit as st
from pymongo.errors import PyMongoError


def render_edit_member_form(collection):
    """
    Renders the Edit/Manage Member interface.
    Features:
    - Search by name (Exact match preferred)
    - Disambiguation: Handles multiple people with the same name.
    - Edit Form: Includes Association, Relationship, and Timestamps.
    """
    
    # --- 1. HEADER & RESET LOGIC ---
    c_head, c_reset = st.columns([4, 1])
    with c_head:
        st.header("👤 Manage Member Details")
    with c_reset:
        if st.button("🔄 Reset", type="tertiary", help="Clear current selection"):
            # Clear all related session states
            keys_to_clear = ['current_person', 'search_candidates', 'is_editing', 'confirm_delete']
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # --- 2. SEARCH SECTION ---
    # Only show search if we haven't selected a person yet
    if 'current_person' not in st.session_state and 'search_candidates' not in st.session_state:
        with st.container():
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                search_query = st.text_input(
                    "Find Person", 
                    placeholder="Enter name (e.g. Satyam Anand)...", 
                    label_visibility="collapsed",
                    key="edit_search_box"
                )
            with search_col2:
                search_btn = st.button("🔍 Search", use_container_width=True, key="edit_search_btn")

        # Handle Search Click
        if search_btn and search_query:
            query_str = search_query.strip()
            # Regex for case-insensitive exact match anchor
            candidates = list(collection.find({"name": {"$regex": f"^{query_str}$", "$options": "i"}}))

            if not candidates:
                st.error(f"❌ No record found for '{query_str}'")
            
            elif len(candidates) == 1:
                # EXACT MATCH -> Select directly
                st.session_state['current_person'] = candidates[0]
                st.session_state['is_editing'] = False
                st.toast(f"✅ Found {candidates[0]['name']}")
                st.rerun()
                
            else:
                # MULTIPLE MATCHES -> Ask user
                st.session_state['search_candidates'] = candidates
                st.rerun()

    # --- 3. DISAMBIGUATION (If multiple results found) ---
    if 'search_candidates' in st.session_state and 'current_person' not in st.session_state:
        st.warning(f"⚠️ Found {len(st.session_state['search_candidates'])} people with that name.")
        
        candidates = st.session_state['search_candidates']
        options_map = {}
        display_options = []
        
        for p in candidates:
            # Build a helpful label: "Name (s/o Father) | Spouse: X"
            parents = p.get('parents', [])
            father = parents[0] if parents else "Unknown"
            spouse = p.get('spouse', 'N/A')
            assoc = p.get('association', 'N/A')
            
            label = f"{p['name']} (s/o {father}) | Spouse: {spouse} | {assoc}"
            display_options.append(label)
            options_map[label] = p

        selected_label = st.selectbox(
            "Please select the correct person to edit:", 
            options=display_options,
            key="disambiguation_select"
        )
        
        c_confirm, c_cancel = st.columns([1, 1])
        with c_confirm:
            if st.button("✅ Confirm Selection", type="primary", use_container_width=True):
                st.session_state['current_person'] = options_map[selected_label]
                del st.session_state['search_candidates'] # Cleanup
                st.session_state['is_editing'] = False
                st.rerun()
        with c_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state['search_candidates']
                st.rerun()

    # --- 4. DISPLAY / EDIT SECTION ---
    if 'current_person' in st.session_state:
        person = st.session_state['current_person']
        st.divider()

        # CHECK: Are we in Edit Mode?
        if not st.session_state.get('is_editing', False):
            # --- VIEW MODE (Read Only) ---
            st.subheader(f"📄 {person['name']}")
            st.caption(f"ID: {person.get('slug', 'N/A')}") # Debug info
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Gender:** {person.get('gender', 'N/A')}")
                st.markdown(f"**Spouse:** {person.get('spouse', 'None')}")
                st.markdown(f"**Phone:** {person.get('phone', '—')}")
                st.markdown(f"**Association:** {person.get('association', '—')}")
                
            with col_b:
                parents = person.get('parents', [])
                parents_str = ", ".join(parents) if parents else "Unknown"
                st.markdown(f"**Parents:** {parents_str}")
                st.markdown(f"**Work:** {person.get('work', '—')}")

            in_laws = person.get('parents_in_law', [])
            if in_laws:
                st.markdown("---")
                st.markdown(f"**Parents-in-Law:** {', '.join(in_laws)}")

            st.divider()
            
            # Action Buttons
            action_col1, action_col2 = st.columns([1, 1])
            with action_col1:
                if st.button("✏️ Edit Details", use_container_width=True):
                    st.session_state['is_editing'] = True
                    st.rerun()
            
            with action_col2:
                if st.button("🗑️ Delete", type="primary", use_container_width=True):
                    st.session_state['confirm_delete'] = True
                    st.rerun()

            # DELETE CONFIRMATION
            if st.session_state.get('confirm_delete', False):
                st.error(f"⚠️ Are you sure you want to delete **{person['name']}**?")
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    if st.button("✅ YES, DELETE", type="primary", use_container_width=True):
                        try:
                            collection.delete_one({"_id": person['_id']})
                            st.success(f"Deleted {person['name']}")
                            del st.session_state['current_person']
                            del st.session_state['confirm_delete']
                            time.sleep(1)
                            st.rerun()
                        except PyMongoError as e:
                            st.error(f"Error: {e}")
                with d_col2:
                    if st.button("❌ NO, Cancel", use_container_width=True):
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

                # Relationship / Association
                st.markdown("### Relationship & Work")
                assoc_options = ["son", "daughter", "daughter-in-law", "son-in-law"]
                curr_assoc = person.get('association', 'son')
                
                # Logic to handle custom associations not in list
                if curr_assoc not in assoc_options:
                    assoc_options.append(curr_assoc)
                
                assoc_idx = assoc_options.index(curr_assoc) if curr_assoc in assoc_options else 0

                w1, w2 = st.columns(2)
                with w1:
                    new_association = st.selectbox("Association", options=assoc_options, index=assoc_idx)
                with w2:
                    new_phone = st.text_input("Phone Number", value=person.get('phone', ''))
                
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
                    # 1. Prepare Data
                    updated_parents = [p.strip() for p in [new_father, new_mother] if p.strip()]
                    updated_in_laws = [p.strip() for p in [new_father_in_law, new_mother_in_law] if p.strip()]
                    
                    # 2. Slug Generation Logic (with Counter)
                    base_slug = new_name.lower().strip().replace(" ", "-")
                    final_slug = base_slug
                    
                    # Check if this slug is taken by SOMEONE ELSE
                    # We look for a doc with this slug where _id is NOT the current person's _id
                    collision = collection.find_one({"slug": final_slug, "_id": {"$ne": person['_id']}})
                    
                    counter = 1
                    while collision:
                        # Collision found! Append counter and try again
                        final_slug = f"{base_slug}-{counter}"
                        collision = collection.find_one({"slug": final_slug, "_id": {"$ne": person['_id']}})
                        counter += 1
                    
                    # At this point, final_slug is unique to this person

                    current_timestamp = datetime.now(timezone.utc)
                    current_user = st.session_state.get("user_name", "Admin").title()

                    update_payload = {
                        "slug": final_slug,  # <--- Now safe to update!
                        "name": new_name.strip(),
                        "gender": new_gender,
                        "spouse": new_spouse.strip(),
                        "parents": updated_parents,
                        "parents_in_law": updated_in_laws, 
                        "phone": new_phone.strip(),
                        "work": new_work.strip(),
                        "association": new_association,
                        "updated_at": current_timestamp,
                        "updated_by": current_user
                    }

                    # 3. DB Update
                    collection.update_one({"_id": person['_id']}, {"$set": update_payload})
                    
                    # Update local state
                    st.session_state['current_person'].update(update_payload)
                    st.session_state['is_editing'] = False 
                    
                    st.success(f"✅ Details updated! (ID: {final_slug})")
                    time.sleep(1) 
                    st.rerun()
                    
                except PyMongoError as e:
                    st.error(f"Update failed: {e}")
