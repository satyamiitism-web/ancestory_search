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

    parents = [get_person(p) for p in person.get("parents", [])]
    parents = [p for p in parents if p]

    grandparents = []
    for parent in parents:
        gp_names = parent.get("parents", [])
        for gp_name in gp_names:
            gp = get_person(gp_name)
            if gp:
                grandparents.append(gp)

    target_name_original = person['name']
    children_cursor = FAMILY_COLLECTION.find({"parents": target_name_original})
    children = list(children_cursor)

    spouse_name = person.get("spouse", "")
    spouse = get_person(spouse_name) if spouse_name else None

    return {
        "target": person,
        "spouse": spouse,
        "parents": parents,
        "grandparents": grandparents,
        "children": children
    }
