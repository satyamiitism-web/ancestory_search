import plotly.graph_objects as go
import streamlit as st

from data.database import FAMILY_COLLECTION


def create_gauge_chart(score):
    """Generates a speedometer-style gauge chart for profile strength."""
    
    # Determine color based on score
    if score >= 80:
        bar_color = "#2ecc71" # Green
    elif score >= 50:
        bar_color = "#f1c40f" # Yellow
    else:
        bar_color = "#e74c3c" # Red

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'suffix': "%", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "gray"},
            'bar': {'color': bar_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(231, 76, 60, 0.1)'},
                {'range': [50, 80], 'color': 'rgba(241, 196, 15, 0.1)'},
                {'range': [80, 100], 'color': 'rgba(46, 204, 113, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    # Clean layout to remove margins and make it transparent
    fig.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)",
        font = {'color': "gray", 'family': "Arial"},
        margin = dict(l=20, r=20, t=30, b=20),
        height = 150  # Compact height
    )
    return fig


# --- MODULE 1: DATA HELPERS ---
async def fetch_searchable_members():
    """
    Fetches minimal member data needed for the search dropdown.
    Returns: 
        (list of display strings, dict mapping display string -> slug)
    """
    raw_members = list(FAMILY_COLLECTION.find({}, {
        "name": 1, "slug": 1, "association": 1,
        "parents": 1, "spouse": 1, "parents_in_law": 1,
        "gender": 1, "_id": 0
    }).sort("name", 1))

    display_options = []
    label_map = {}

    for m in raw_members:
        label = await _generate_member_label(m)
        slug = m.get('slug') or m.get('name') # Fallback for old data
        
        display_options.append(label)
        label_map[label] = slug

    return display_options, label_map

async def _generate_member_label(m):
    """Internal helper to generate the descriptive dropdown label."""
    name = m.get('name')
    assoc = str(m.get('association', '')).lower().strip()
    
    # Helper to safely get the first item from a list or string
    def get_first(field):
        val = m.get(field)
        if isinstance(val, list) and val: return val[0]
        if isinstance(val, str): return val
        return None

    spouse = get_first('spouse')
    father = get_first('parents')
    father_in_law = get_first("parents_in_law")
    
    relation_suffix = ""

    # Logic to create context string (e.g., "w/o Name" or "s/o Name")
    if "daughter-in-law" in assoc:
        relation_suffix = f"(d/o-in-law of {father_in_law})" if father_in_law else f"(w/o {spouse})"
    
    elif "son-in-law" in assoc:
        if father_in_law: 
            relation_suffix = f"(s/o-in-law of {father_in_law})"
        elif spouse:
            relation_suffix = f"(h/o {spouse})"
    
    else:
        # Standard son/daughter logic
        is_female = "daughter" in assoc or "beti" in assoc or "F" in str(m.get('gender','')).lower()
        
        if father:
            prefix = "d/o" if is_female else "s/o"
            relation_suffix = f"({prefix} {father})"
        elif spouse:
            prefix = "w/o" if is_female else "h/o"
            relation_suffix = f"({prefix} {spouse})"

    return f"{name} {relation_suffix}".strip()


# --- MODULE 2: UI COMPONENTS ---
async def render_profile_header(target, score, missing_fields):
    """Renders the top section with Name, Badges, and Graphical Score."""
    
    # Adjust columns to give the chart more space
    col_main, col_chart = st.columns([0.7, 0.3])
    
    with col_main:
        st.markdown(f"## 👤 {target['name']}")
        
        # Prepare Badge Data
        gender_txt = "Male" if target.get('gender') == "M" else "Female"
        gender_icon = "♂️" if gender_txt == "Male" else "♀️"
        phone = target.get('phone', 'Not Available') if target.get('phone') else "Not Available"
        work = target.get('work', 'Not Available') if target.get("work") else "Not Available"

        # CSS for Badges
        badge_style = """
        display: inline-flex; align-items: center; 
        background-color: rgba(128, 128, 128, 0.15); 
        padding: 4px 12px; border-radius: 20px; 
        margin-right: 10px; font-size: 0.9em;
        """
        
        st.markdown(
            f"""
            <div style="margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 10px;">
                <span style="{badge_style}"><span style="margin-right: 6px;">{gender_icon}</span> {gender_txt}</span>
                <span style="{badge_style}"><span style="margin-right: 6px;">📞</span> {phone}</span>
                <span style="{badge_style}"><span style="margin-right: 6px;">💼</span> {work}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # "What's Missing" Expander (Only show if not perfect)
        if score < 100 and missing_fields:
            with st.expander("💡 Improve this profile"):
                st.caption("Add the following details to reach 100%:")
                for field in missing_fields:
                    st.markdown(f"- ❌ **{field}**")

    with col_chart:
        # Render the Plotly Gauge
        st.plotly_chart(create_gauge_chart(score), use_container_width=True, config={'displayModeBar': False})

async def render_relationship_grid(results):
    """Renders the 2x2 grid of family connections."""
    
    # Helper to format lists of names
    def format_list(person_list):
        if not person_list: return "—"
        return ", ".join([p['name'] for p in person_list])

    spouse_val = results['spouse']['name'] if results['spouse'] else "—"
    
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.info(f"**❤️ Spouse**\n\n{spouse_val}")
    with r1c2:
        st.success(f"**👶 Children**\n\n{format_list(results['children'])}")
        
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.warning(f"**👪 Parents**\n\n{format_list(results['parents'])}")
    with r2c2:
        st.error(f"**👴👵 Grandparents**\n\n{format_list(results['grandparents'])}")


# --- MODULE 3: LOGIC & MAIN VIEW ---
async def calculate_profile_score(target, results):
    """
    Calculates score and identifies missing data.
    Returns: (score, list_of_missing_fields)
    """
    score = 0
    missing = []
    
    # Define criteria
    weights = {
        'Basic Info': {'points': 20, 'check': target.get('name') and target.get('gender')},
        'Parents Linked': {'points': 30, 'check': bool(results.get('parents'))},
        'Contact Info': {'points': 20, 'check': str(target.get('phone', '')).strip() not in ['-', '—', 'N/A', 'None', '']},
        'Work Info': {'points': 20, 'check': str(target.get('work', '')).strip() not in ['-', '—', 'N/A', 'None', '']},
        'Spouse/Children': {'points': 10, 'check': bool(results.get('spouse')) or bool(results.get('children'))}
    }

    for label, data in weights.items():
        if data['check']:
            score += data['points']
        else:
            missing.append(label)

    return min(score, 100), missing

async def _display_family_results(results):
    """Orchestrates the display of the selected member's profile."""
    target = results['target']
    
    # 1. Calc Score & Status
    score, missing_fields = await calculate_profile_score(target, results)

    st.divider()
    
    # 2. Render UI
    await render_profile_header(target, score, missing_fields)
    await render_relationship_grid(results)

async def render_search_interface(get_relatives_func):
    """Main Entry Point: Renders the search dropdown and handles selection."""
    st.header("📇 View Member Details")

    # 1. Get Data
    display_options, label_map = await fetch_searchable_members()

    # 2. Render Dropdown
    selected_label_list = st.multiselect(
        "Search Family Member",
        options=display_options,
        placeholder="Type to search...",
        max_selections=1,
        label_visibility="collapsed"
    )

    # 3. Handle Selection
    if selected_label_list:
        selected_slug = label_map[selected_label_list[0]]

        with st.spinner("Fetching details..."):
            results = await get_relatives_func(selected_slug)

        if results:
            await _display_family_results(results)
        else:
            st.error(f"Could not find details for ID: {selected_slug}")
