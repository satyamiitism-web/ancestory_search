from data.database import FAMILY_DB


def get_person(name):
    """Safe lookup function"""
    return FAMILY_DB.get(name.lower().strip())

# --- 2. Logic to Find Relatives ---
def get_relatives(person_name):
    person = get_person(person_name)
    if not person:
        return None

    # Get immediate parents
    parents = [get_person(p) for p in person.get("parents", [])]
    parents = [p for p in parents if p] # Filter out missing data

    # Get grandparents (parents of parents)
    grandparents = []
    for parent in parents:
        gp_names = parent.get("parents", [])
        for gp_name in gp_names:
            gp = get_person(gp_name)
            if gp:
                grandparents.append(gp)

    children = []
    target_name_original = person['name'] # e.g. "Satyam Anand"
    
    for key, data in FAMILY_DB.items():
        # Check if target is in this person's parent list
        # We check both exact match and lowercase match to be safe
        db_parents = [p.lower() for p in data.get("parents", [])]
        if target_name_original.lower() in db_parents:
            children.append(data)

    return {
        "target": person,
        "spouse": get_person(person.get("spouse", "")),
        "parents": parents,
        "grandparents": grandparents,
        "children": children
    }
