import streamlit as st
from data.database import FAMILY_COLLECTION 

def render_search_interface(get_relatives_func):
    """
    Renders search with context based on 'Association' type.
    Uses SLUG to ensure the correct duplicate member is shown.
    """
    st.header("📇 View Member Details")

    # --- 1. Fetch Data (Must include 'slug') ---
    raw_members = list(FAMILY_COLLECTION.find({}, {
        "name": 1, 
        "slug": 1,  # <--- CRITICAL: Fetch Unique ID
        "association": 1,
        "parents": 1, 
        "spouse": 1,
        "parents_in_law": 1,
        "gender": 1,
        "_id": 0
    }).sort("name", 1))

    # --- 2. Build Labels ---
    # Map: "Display Label" -> "Unique Slug"
    label_to_slug_map = {}
    display_options = []

    for m in raw_members:
        name = m.get('name')
        slug = m.get('slug') # Unique ID
        
        # If no slug exists (old data), fall back to name, but warn internally
        if not slug: 
            slug = name 

        assoc = str(m.get('association', '')).lower().strip()
        
        # Helpers
        def get_first(field):
            val = m.get(field)
            if isinstance(val, list) and val: return val[0]
            if isinstance(val, str): return val
            return None

        spouse_name = get_first('spouse')
        father_name = get_first('parents')
        father_in_law_name = get_first("parents_in_law")
        
        relation_suffix = ""

        # --- LOGIC START (Same as your logic) ---
        if "daughter-in-law" in assoc:
            if father_in_law_name:
                 relation_suffix = f"(d/o-in-law of {father_in_law_name})"
            else:
                relation_suffix = f"(w/o {spouse_name})"

        elif "son-in-law" in assoc:
            if father_in_law_name: 
                relation_suffix = f"(s/o-in-law of {father_in_law_name})"
            elif spouse_name:
                relation_suffix = f"(h/o {spouse_name})"

        else:
            if father_name:
                if "daughter" in assoc or "beti" in assoc or "female" in str(m.get('gender','')).lower():
                    prefix = "d/o"
                else:
                    prefix = "s/o"
                relation_suffix = f"({prefix} {father_name})"
            
            elif spouse_name:
                 prefix = "w/o" if "female" in str(m.get('gender','')).lower() else "h/o"
                 relation_suffix = f"({prefix} {spouse_name})"
        # --- LOGIC END ---

        full_label = f"{name} {relation_suffix}".strip()
        
        # Add to list and map
        display_options.append(full_label)
        label_to_slug_map[full_label] = slug  # Store SLUG here, not name

    # --- 3. Render Widget ---
    selected_label_list = st.multiselect(
        "Search Family Member",
        options=display_options,
        placeholder="Type to search...",
        max_selections=1,
        label_visibility="collapsed"
    )

    # --- 4. Handle Selection ---
    if selected_label_list:
        label_selected = selected_label_list[0]
        
        # Retrieve the SLUG
        selected_slug = label_to_slug_map[label_selected]

        with st.spinner(f"Fetching details..."):
            results = get_relatives_func(selected_slug)

        if results:
            _display_family_results(results)
        else:
            st.error(f"Could not find details for ID: {selected_slug}")


def _display_family_results(results):
    """Internal helper to display the results nicely."""
    
    target = results['target']
    
    # --- Data Extraction ---
    # safely get phone/work, defaulting to dash if missing
    phone = target.get('phone', '—')
    work = target.get('work', '—')
    gender = target.get('gender', 'N/A')

    # --- Header Section ---
    st.divider()
    st.subheader(f"👤 {target['name']}")
    
    # NEW: Metadata Row (Gender | Phone | Work)
    m1, m2, m3 = st.columns(3)
    with m1:
        gender_icon = "👨" if gender == "M" else "👩" 
        st.caption(f"{gender_icon} **Gender:** {gender}")
    with m2:
        st.markdown(f"📞 **Phone:** {phone}")
    with m3:
        st.markdown(f"💼 **Work:** {work}")

    # --- Relationship Data Preparation ---
    def format_list(person_list):
        if not person_list:
            return "—"
        return ", ".join([f"**{p['name']}**" for p in person_list])

    spouse_val = f"**{results['spouse']['name']}**" if results['spouse'] else "—"
    children_val = format_list(results['children'])
    parents_val = format_list(results['parents'])
    grandparents_val = format_list(results['grandparents'])

    # --- Visual Cards Layout ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.info(f"❤️ **Spouse**\n\n{spouse_val}")
        st.warning(f"👪 **Parents**\n\n{parents_val}")
        
    with c2:
        st.success(f"👶 **Children**\n\n{children_val}")
        st.error(f"👴👵 **Grandparents**\n\n{grandparents_val}")
