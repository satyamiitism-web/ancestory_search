import streamlit as st
import pandas as pd

def render_database_view(collection):
    """
    Fetches all documents from the collection, cleans specific columns, 
    and displays them in a Streamlit dataframe.
    """
    # Fetch all data from the collection
    data = list(collection.find())

    if data:
        df = pd.DataFrame(data)

        # Drop '_id' and 'slug' columns if they exist
        # errors='ignore' prevents crashing if the columns are missing
        columns_to_drop = ['_id', 'slug']
        df = df.drop(columns=columns_to_drop, errors='ignore')

        # Display the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("The database is currently empty.")
