from data.database import FAMILY_COLLECTION

def get_relatives(slug):
    """
    Fetches relatives for a person based on their unique SLUG.
    
    Args:
        slug (str): The unique identifier (e.g., 'amit-kumar-1') of the person.
    
    Returns:
        dict: A dictionary containing the target person and all found relatives.
    """
    
    # 1. Fetch the TARGET PERSON by SLUG (Precision Lookup)
    person = FAMILY_COLLECTION.find_one({"slug": slug})
    
    if not person:
        # Fallback: If slug logic fails or old code calls with name, try name lookup
        # This prevents the app from crashing during transition
        person = FAMILY_COLLECTION.find_one({"name": slug})
        if not person:
            return None

    # We need the Name String to find relationships because your DB currently
    # links people via strings (e.g., "parents": ["Suresh"])
    target_name_string = person['name']

    # --- Helper: Name-based Lookup ---
    # Used for looking up parents/spouses referenced by name string
    def get_by_name(name_str):
        if not name_str: return None
        # Note: If multiple people have the same name, this picks the first one.
        # This is a limitation of name-based linking.
        return FAMILY_COLLECTION.find_one({"name": name_str})

    # 2. Parents
    parents = []
    raw_parents = person.get("parents", [])
    for p_name in raw_parents:
        p_doc = get_by_name(p_name)
        if p_doc:
            parents.append(p_doc)

    # 3. Grandparents
    grandparents = []
    for parent in parents:
        gp_names = parent.get("parents", [])
        for gp_name in gp_names:
            gp_doc = get_by_name(gp_name)
            if gp_doc:
                grandparents.append(gp_doc)

    # 4. Children
    # Find all docs where 'parents' array contains the target's NAME
    target_name_string = person['name']
    spouse_name_string = person.get('spouse')
    raw_children = list(FAMILY_COLLECTION.find({"parents": target_name_string}))
    
    children = []
    
    for child in raw_children:
        child_parents = child.get('parents', [])
        
        # LOGIC: If I have a spouse, and this child has 2 parents, 
        # check if the OTHER parent matches MY spouse.
        
        if spouse_name_string and len(child_parents) > 1:
            # Find the parent that is NOT me
            # (Handle case where both parents might be named Renu, rare but possible)
            other_parents = [p for p in child_parents if p != target_name_string]
            
            if other_parents:
                other_parent = other_parents[0] # Take the first co-parent
                
                # STRING COMPARISON: Loosely check if spouses match
                # e.g. "Mukesh Kumar" vs "Mukesh Kumar Sharma"
                # If they are completely different, it's likely the WRONG Renu's child.
                
                # Check 1: Exact Match
                if other_parent == spouse_name_string:
                    children.append(child)
                    
                # Check 2: Partial Match (e.g. Mukesh vs Mukesh Kumar)
                elif other_parent in spouse_name_string or spouse_name_string in other_parent:
                     children.append(child)
                     
                else:
                    # Debug: "Skipping child {child['name']} because co-parent {other_parent} != {spouse_name_string}"
                    continue 
            else:
                # No co-parent found (or I am listed twice?), safe to include or investigate
                children.append(child)
        else:
            # If I have no spouse listed, or child only has 1 parent listed, 
            # we can't filter safely, so we include them.
            children.append(child)

    # 5. Grandchildren
    grandchildren = []
    for child in children:
        child_name = child['name']
        # Find anyone who lists THIS child as a parent
        gc_cursor = FAMILY_COLLECTION.find({"parents": child_name})
        gcs = list(gc_cursor)
        
        # Tag them for context
        for gc in gcs:
            gc['child_of'] = child_name
            grandchildren.append(gc)

    # 6. Spouse
    spouse_name = person.get("spouse", "")
    spouse = get_by_name(spouse_name) if spouse_name else None

    # 7. Parents-in-Law
    parents_in_law = []
    raw_in_laws = person.get("parents_in_law", [])
    
    # Logic: If not explicitly stored, try to get Spouse's parents
    if not raw_in_laws and spouse:
        raw_in_laws = spouse.get("parents", [])

    for pl_name in raw_in_laws:
        pl_doc = get_by_name(pl_name)
        if pl_doc:
            parents_in_law.append(pl_doc)
        else:
            # Create dummy object if DB record missing but name is known
            parents_in_law.append({'name': pl_name, 'gender': 'Unknown'})

    # 8. Children-in-Law
    children_in_law = []
    for child in children:
        c_spouse_name = child.get("spouse")
        if c_spouse_name:
            c_spouse = get_by_name(c_spouse_name)
            if c_spouse:
                c_spouse['spouse_of'] = child['name']
                children_in_law.append(c_spouse)
            else:
                children_in_law.append({
                    'name': c_spouse_name, 
                    'gender': 'Unknown', 
                    'spouse_of': child['name']
                })

    return {
        "target": person,
        "spouse": spouse,
        "parents": parents,
        "grandparents": grandparents,
        "children": children,
        "grandchildren": grandchildren,
        "parents_in_law": parents_in_law,
        "children_in_law": children_in_law
    }
