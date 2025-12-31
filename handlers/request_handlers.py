from data.database import FAMILY_COLLECTION


def get_person(person_name):
    """Safe lookup function"""
    name_query = person_name.lower().strip()
    family_data = FAMILY_COLLECTION.find_one({"slug": name_query})
    return family_data

def get_relatives(person_name):
    person = get_person(person_name)
    if not person:
        return None

    # 1. Parents
    parents = [get_person(p) for p in person.get("parents", [])]
    parents = [p for p in parents if p]

    # 2. Grandparents
    grandparents = []
    for parent in parents:
        gp_names = parent.get("parents", [])
        for gp_name in gp_names:
            gp = get_person(gp_name)
            if gp:
                grandparents.append(gp)

    # 3. Children
    target_name_original = person['name']
    children_cursor = FAMILY_COLLECTION.find({"parents": target_name_original})
    children = list(children_cursor)

    # --- 4. Grandchildren (NEW) ---
    grandchildren = []
    for child in children:
        child_name = child['name']
        # Find anyone who lists this child as a parent
        gc_cursor = FAMILY_COLLECTION.find({"parents": child_name})
        gcs = list(gc_cursor)
        
        # Tag them so we know which child they belong to (essential for the graph)
        for gc in gcs:
            gc['child_of'] = child_name
            grandchildren.append(gc)

    # 5. Spouse
    spouse_name = person.get("spouse", "")
    spouse = get_person(spouse_name) if spouse_name else None

    # 6. Parents-in-Law
    parents_in_law = []
    raw_in_laws = person.get("parents_in_law", [])
    if not raw_in_laws and spouse:
        raw_in_laws = spouse.get("parents", [])

    for pl_name in raw_in_laws:
        pl_doc = get_person(pl_name)
        if pl_doc:
            parents_in_law.append(pl_doc)
        else:
            parents_in_law.append({'name': pl_name, 'gender': 'Unknown'})

    # 7. Children-in-Law
    children_in_law = []
    for child in children:
        c_spouse_name = child.get("spouse")
        if c_spouse_name:
            c_spouse = get_person(c_spouse_name)
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
        "grandchildren": grandchildren, # <--- Added
        "parents_in_law": parents_in_law,
        "children_in_law": children_in_law
    }
