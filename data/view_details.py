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
    """Internal helper to display the results with a clean Profile Score."""
    
    target = results['target']
    
    # --- 1. Calculate Score (Same logic as before) ---
    def calculate_score(member_data):
        score = 0
        weights = {'basic_info': 20, 'parents': 30, 'spouse': 5, 
                   'children': 5, 'contact': 20, 'work': 20}

        if member_data.get('name') and member_data.get('gender'): score += weights['basic_info']
        if results.get('parents'): score += weights['parents']
        if results.get('spouse'): score += weights['spouse']
        if results.get('children'): score += weights['children']
        
        raw_phone = str(member_data.get('phone', '')).strip()
        if raw_phone and raw_phone not in ['-', '—', 'N/A', 'None']: score += weights['contact']
            
        raw_work = str(member_data.get('work', '')).strip()
        if raw_work and raw_work not in ['-', '—', 'N/A', 'None']: score += weights['work']

        return min(score, 100) # Cap at 100

    profile_score = calculate_score(target)

    # --- 2. Determine Status ---
    if profile_score >= 80:
        delta_color = "normal" # Green in Streamlit metric
        status_label = "🌟 Excellent"
    elif profile_score >= 50:
        delta_color = "off"   # Gray/Neutral
        status_label = "⚠️ Good"
    else:
        delta_color = "inverse" # Red
        status_label = "🔴 Incomplete"

    # --- 3. CLEAN HEADER LAYOUT ---
    st.divider()
    
    # Create a 2-column layout: Left for Name/Bio, Right for Score Card
    col_main, col_score = st.columns([0.8, 0.2])
    
    with col_main:
        # Big Name Header
        st.markdown(f"## 👤 {target['name']}")

        gender_txt = "Male" if target.get('gender') == "M" else "Female"
        gender_icon = "👨" if gender_txt == "M" else "👩"
        phone = target.get('phone', 'Not Available')
        work = target.get('work', 'Not Available')

        badge_style = """
        display: inline-flex;
        align-items: center;
        background-color: rgba(128, 128, 128, 0.15); 
        padding: 4px 12px;
        border-radius: 20px;
        margin-right: 10px;
        font-size: 0.9em;
        """
        
        # Render clean HTML badges
        st.markdown(
            f"""
            <div style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">
                <span style="{badge_style}">
                    <span style="margin-right: 6px;">{gender_icon}</span> {gender_txt}
                </span>
                <span style="{badge_style}">
                    <span style="margin-right: 6px;">📞</span> {phone}
                </span>
                <span style="{badge_style}">
                    <span style="margin-right: 6px;">💼</span> {work}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_score:
        # Use st.metric for a clean, professional stat look
        st.metric(
            label="Profile Strength", 
            value=f"{profile_score}%", 
            delta=status_label,
            delta_color=delta_color
        )

    # --- 4. Relationship Cards (Standardized Grid) ---
    def format_list(person_list):
        if not person_list: return "—"
        return ", ".join([p['name'] for p in person_list]) # Removed bolding for cleaner look inside colored boxes

    spouse_val = results['spouse']['name'] if results['spouse'] else "—"
    
    # Row 1
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.info(f"**❤️ Spouse**\n\n{spouse_val}")
    with r1c2:
        st.success(f"**👶 Children**\n\n{format_list(results['children'])}")
        
    # Row 2
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.warning(f"**👪 Parents**\n\n{format_list(results['parents'])}")
    with r2c2:
        st.error(f"**👴👵 Grandparents**\n\n{format_list(results['grandparents'])}")
