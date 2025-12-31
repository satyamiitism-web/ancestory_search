from datetime import datetime
import streamlit as st
from data.database import EVENTS_COLLECTION

import streamlit as st
from datetime import datetime

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

