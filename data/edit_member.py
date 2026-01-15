import time
from datetime import datetime, timezone

import streamlit as st
from pymongo.errors import PyMongoError


async def render_header_with_reset():
    """Renders the header and the reset button to clear session state."""
    c_head, c_reset = st.columns([4, 1])
    with c_head:
        st.header("👤 Manage Member Details")
    with c_reset:
        if st.button("🔄 Reset", type="tertiary", help="Clear current selection"):
            keys_to_clear = ['current_person', 'search_candidates', 'is_editing', 'confirm_delete']
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

async def render_search_box(collection):
    """Renders the search box and handles the query logic."""
    with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
            query = st.text_input("Find Person", placeholder="Enter name...", label_visibility="collapsed", key="edit_search_box")
        with c2:
            search_btn = st.button("🔍 Search", use_container_width=True, key="edit_search_btn")

        if search_btn and query:
            q_str = query.strip()
            # Regex for case-insensitive exact match
            candidates = list(collection.find({"name": {"$regex": f"^{q_str}$", "$options": "i"}}))

            if not candidates:
                st.error(f"❌ No record found for '{q_str}'")
            elif len(candidates) == 1:
                st.session_state['current_person'] = candidates[0]
                st.session_state['is_editing'] = False
                st.toast(f"✅ Found {candidates[0]['name']}")
                st.rerun()
            else:
                st.session_state['search_candidates'] = candidates
                st.rerun()

async def render_disambiguation_widget():
    """Renders a selectbox if multiple people are found."""
    candidates = st.session_state['search_candidates']
    st.warning(f"⚠️ Found {len(candidates)} people with that name.")
    
    options_map = {}
    display_options = []
    
    for p in candidates:
        parents = p.get('parents', [])
        father = parents[0] if parents else "Unknown"
        spouse = p.get('spouse', 'N/A')
        label = f"{p['name']} (s/o {father}) | Spouse: {spouse} | {p.get('association', 'N/A')}"
        display_options.append(label)
        options_map[label] = p

    selected = st.selectbox("Please select the correct person:", options=display_options, key="disambiguation_select")
    
    c1, c2 = st.columns([1, 1])
    if c1.button("✅ Confirm", type="primary", use_container_width=True):
        st.session_state['current_person'] = options_map[selected]
        del st.session_state['search_candidates']
        st.session_state['is_editing'] = False
        st.rerun()
    
    if c2.button("❌ Cancel", use_container_width=True):
        del st.session_state['search_candidates']
        st.rerun()


async def handle_delete(collection, person):
    """Handles the deletion of a member."""
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

async def generate_unique_slug(collection, name, person_id):
    """Generates a unique slug for the person."""
    base_slug = name.lower().strip().replace(" ", "-")
    final_slug = base_slug
    
    # Check for collision with OTHER people (exclude self)
    collision = collection.find_one({"slug": final_slug, "_id": {"$ne": person_id}})
    counter = 1
    
    while collision:
        final_slug = f"{base_slug}-{counter}"
        collision = collection.find_one({"slug": final_slug, "_id": {"$ne": person_id}})
        counter += 1
    
    return final_slug

async def save_updates(collection, person, form_data):
    """Validates and saves the form data to MongoDB."""
    try:
        new_name = form_data['name']
        final_slug = await generate_unique_slug(collection, new_name, person['_id'])
        
        timestamp = datetime.now(timezone.utc)
        user = st.session_state.get("user_name", "Admin").title()
        
        payload = {
            "slug": final_slug,
            "name": new_name,
            "gender": form_data['gender'],
            "spouse": form_data['spouse'],
            "parents": form_data['parents'],
            "parents_in_law": form_data['in_laws'],
            "phone": form_data['phone'],
            "work": form_data['work'],
            "association": form_data['association'],
            "updated_at": timestamp,
            "updated_by": user
        }
        
        collection.update_one({"_id": person['_id']}, {"$set": payload})
        
        # Update Session State
        st.session_state['current_person'].update(payload)
        st.session_state['is_editing'] = False
        st.success(f"✅ Updated! (ID: {final_slug})")
        time.sleep(1)
        st.rerun()
        
    except PyMongoError as e:
        st.error(f"Update failed: {e}")


async def render_view_mode(person, collection):
    """Renders the Read-Only view of a person."""
    st.subheader(f"📄 {person['name']}")
    st.caption(f"ID: {person.get('slug', 'N/A')}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Gender:** {person.get('gender', 'N/A')}")
        st.markdown(f"**Spouse:** {person.get('spouse', '-')}")
        st.markdown(f"**Phone:** {person.get('phone', '—')}")
        st.markdown(f"**Association:** {person.get('association', '—')}")
    with c2:
        parents = person.get('parents', [])
        st.markdown(f"**Parents:** {', '.join(parents) if parents else 'Unknown'}")
        st.markdown(f"**Work:** {person.get('work', '—')}")

    in_laws = person.get('parents_in_law', [])
    if in_laws:
        st.markdown("---")
        st.markdown(f"**Parents-in-Law:** {', '.join(in_laws)}")

    st.divider()
    
    # Action Buttons
    ac1, ac2 = st.columns([1, 1])
    if ac1.button("✏️ Edit Details", use_container_width=True):
        st.session_state['is_editing'] = True
        st.rerun()
    
    if ac2.button("🗑️ Delete", type="primary", use_container_width=True):
        st.session_state['confirm_delete'] = True
        st.rerun()

    # Delete Confirmation
    if st.session_state.get('confirm_delete', False):
        st.error(f"⚠️ Confirm deletion of **{person['name']}**?")
        d1, d2 = st.columns(2)
        with d1: await handle_delete(collection, person)
        with d2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state['confirm_delete'] = False
                st.rerun()

async def render_edit_form(person, collection):
    """Renders the Edit Form with side-by-side layouts."""
    st.subheader(f"✏️ Editing: {person['name']}")
    
    with st.form("update_form"):
        # ROW 1: Name
        new_name = st.text_input("Full Name", value=person['name'])
        
        # ROW 2: Gender & Spouse (Side by Side)
        c1, c2 = st.columns(2)
        with c1:
            g_opts = ["M", "F", "Other"]
            curr_g = person.get('gender', 'M')
            # Safe index lookup
            idx = g_opts.index(curr_g) if curr_g in g_opts else 0
            new_gender = st.selectbox("Gender", g_opts, index=idx)
        with c2:
            new_spouse = st.text_input("Spouse Name", value=person.get('spouse', ''))

        # ROW 3: Parents (Side by Side)
        st.markdown("### Parents")
        curr_p = person.get('parents', [])
        p1_val = curr_p[0] if len(curr_p) > 0 else ""
        p2_val = curr_p[1] if len(curr_p) > 1 else ""
        
        pc1, pc2 = st.columns(2)
        with pc1:
            new_father = st.text_input("Father", value=p1_val)
        with pc2:
            new_mother = st.text_input("Mother", value=p2_val)

        # ROW 4: In-Laws (Side by Side)
        st.markdown("### Parent-in-laws")
        curr_pil = person.get('parents_in_law', [])
        pil1_val = curr_pil[0] if len(curr_pil) > 0 else ""
        pil2_val = curr_pil[1] if len(curr_pil) > 1 else ""

        pil_c1, pil_c2 = st.columns(2)
        with pil_c1:
            new_father_in_law = st.text_input("Father-in-law", value=pil1_val)
        with pil_c2:
            new_mother_in_law = st.text_input("Mother-in-law", value=pil2_val)

        # ROW 5: Association & Phone (Side by Side)
        st.markdown("### Relationship & Work")
        assoc_opts = ["son", "daughter", "daughter-in-law", "son-in-law"]
        curr_assoc = person.get('association', 'son')
        if curr_assoc not in assoc_opts: assoc_opts.append(curr_assoc)
        
        rc1, rc2 = st.columns(2)
        with rc1:
            new_assoc = st.selectbox("Association", assoc_opts, 
                                     index=assoc_opts.index(curr_assoc) if curr_assoc in assoc_opts else 0)
        with rc2:
            new_phone = st.text_input("Phone", value=person.get('phone', ''))
        
        # ROW 6: Work (Full Width)
        new_work = st.text_input("Work Details", value=person.get('work', ''))

        st.divider()
        
        # Buttons
        b1, b2 = st.columns([1, 1])
        with b1:
            submit = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
        with b2:
            cancel = st.form_submit_button("❌ Cancel", type="secondary", use_container_width=True)

    if cancel:
        st.session_state['is_editing'] = False
        st.rerun()

    if submit:
        # Pack data for logic handler
        form_data = {
            "name": new_name.strip(),
            "gender": new_gender,
            "spouse": new_spouse.strip(),
            "parents": [p.strip() for p in [new_father, new_mother] if p.strip()],
            "in_laws": [p.strip() for p in [new_father_in_law, new_mother_in_law] if p.strip()],
            "association": new_assoc,
            "phone": new_phone.strip(),
            "work": new_work.strip()
        }
        await save_updates(collection, person, form_data)


async def render_edit_member_form(collection):
    """
    Main entry point for the Edit Member Interface.
    Orchestrates components from helper modules.
    """
    
    # 1. Header & Reset
    await render_header_with_reset()

    # 2. Search Logic (Show only if no person selected)
    if 'current_person' not in st.session_state and 'search_candidates' not in st.session_state:
        await render_search_box(collection)

    # 3. Disambiguation (If multiple results)
    if 'search_candidates' in st.session_state and 'current_person' not in st.session_state:
        await render_disambiguation_widget()

    # 4. Display or Edit Logic
    if 'current_person' in st.session_state:
        person = st.session_state['current_person']
        st.divider()
        
        if st.session_state.get('is_editing', False):
            await render_edit_form(person, collection)
        else:
            await render_view_mode(person, collection)
