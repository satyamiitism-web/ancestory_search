from datetime import datetime
from database import EVENTS_COLLECTION

# Define the event data
new_event = {
    "title": "Grand Family Poojan",
    "date": datetime(2025, 4, 10),
    "location": "Naimisharanya Temple",
    "description": "Special pooja for the ancestors.",
    "created_at": datetime.now()
}

EVENTS_COLLECTION.insert_one(new_event)