from datetime import datetime
import streamlit as st
from data.database import EVENTS_COLLECTION

import streamlit as st
from datetime import datetime, time

def render_add_event_form():
    """
    Renders a form to add new events to the MongoDB 'events' collection.
    """
    st.subheader("📅 Add New Event")
    
    with st.form("new_event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Event Title", placeholder="e.g. Holi Milan Samaroh")
            location = st.text_input("Location", placeholder="e.g. Community Hall, Bahlolpur")
            
        with col2:
            event_date = st.date_input("Event Date", min_value=datetime.today())
            event_time = st.time_input("Time (Optional)", value=time(9, 0)) # Default 9:00 AM

        description = st.text_area("Description / Details", placeholder="Enter details about the event...")
        
        submitted = st.form_submit_button("Save Event", type="primary")
        
        if submitted:
            if not title or not location:
                st.error("⚠️ Title and Location are required!")
            else:
                try:
                    # 1. Combine Date and Time into a single datetime object
                    # This is CRITICAL for your "upcoming" logic to work correctly
                    full_datetime = datetime.combine(event_date, event_time)
                    current_user = st.session_state.get("user_name").title()
                    
                    # 2. Create the document object
                    new_event = {
                        "title": title.strip(),
                        "date": full_datetime, # Stored as ISODate in Mongo
                        "location": location.strip(),
                        "description": description.strip(),
                        "created_at": datetime.now(),
                        "created_by": current_user
                    }
                    
                    # 3. Insert into Database
                    EVENTS_COLLECTION.insert_one(new_event)
                    
                    # 4. Success Feedback
                    st.success(f"✅ Event '{title}' added successfully!")
                    
                    # Optional: Rerun to update any sidebar/lists immediately
                    # st.rerun() 
                    
                except Exception as e:
                    st.error(f"❌ Error adding event: {e}")


def render_events_page(events_collection):
    """Renders a full-page timeline view of upcoming events."""
    
    st.header("📅 Upcoming Events")
    st.markdown("---")

    # 1. Get Data
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    events = list(events_collection.find({"date": {"$gte": today}}).sort("date", 1))

    # 2. Handle Empty State
    if not events:
        st.container(border=True).info(
            """
            **No upcoming events scheduled.**
            
            Check back later for updates on family gatherings, poojas, or meetings.
            """
        )
        return

    # 3. Render Timeline
    for event in events:
        # Calculate days remaining for badge
        days_left = (event['date'] - today).days
        
        if days_left == 0:
            status = "🔴 HAPPENING TODAY"
            border_color = "red"
        elif days_left == 1:
            status = "🟠 TOMORROW"
            border_color = "orange"
        else:
            status = f"🟢 IN {days_left} DAYS"
            border_color = "grey"

        # Create the Card
        with st.container(border=True):
            col_date, col_details = st.columns([1, 5])
            
            # Left Column: Big Date Badge
            with col_date:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f0f2f6; 
                        border-radius: 10px; 
                        padding: 10px; 
                        text-align: center;
                        border: 1px solid #ddd;">
                        <span style="font-size: 1.5em; font-weight: bold; display: block; color: #333;">
                            {event['date'].strftime('%d')}
                        </span>
                        <span style="font-size: 0.9em; text-transform: uppercase; color: #666;">
                            {event['date'].strftime('%b')}
                        </span>
                        <span style="font-size: 0.8em; display: block; color: #888;">
                            {event['date'].strftime('%Y')}
                        </span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

            # Right Column: Details
            with col_details:
                # Title and Status Badge
                st.markdown(f"### {event['title']}")
                st.caption(f"**{status}**")
                
                # Location and Description
                st.markdown(f"📍 **Location:** {event['location']}")
                
                if event.get('description'):
                    st.write(event['description'])
                    
                # Optional: Add "Add to Calendar" text copy helper
                st.code(f"{event['title']} on {event['date'].strftime('%Y-%m-%d')} at {event['location']}", language="text")

