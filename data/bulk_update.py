import streamlit as st
import pandas as pd
from datetime import datetime
from .database import FAMILY_COLLECTION # Adjusted import for standard file structure

def render_bulk_update_form():
    """
    Renders a file uploader and processes the CSV to update ANY specific field
    for family members using their Slug as the identifier.
    """
    st.header("📂 Bulk Update Data")
    st.markdown("Upload a CSV file to update **any specific field** for multiple members using their Slug.")

    # 1. FILE UPLOADER
    uploaded_file = st.file_uploader("Upload Update CSV", type=["csv"])

    if uploaded_file:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            # Ensure column names are clean (strip spaces)
            df.columns = df.columns.str.strip()

            st.subheader("1. Preview Data")
            st.dataframe(df.head(), use_container_width=True)

            # 2. COLUMN MAPPING
            st.subheader("2. Map Columns")
            st.info("Map your CSV columns to the Database fields.")
            
            all_cols = df.columns.tolist()
            
            # Smart defaults: Try to find 'slug' automatically
            default_slug_idx = all_cols.index("slug") if "slug" in all_cols else 0
            
            c1, c2, c3 = st.columns(3)
            
            with c1:
                # User selects which CSV column contains the unique slug
                slug_col = st.selectbox("CSV Column for Slug (ID)", all_cols, index=default_slug_idx)
            
            with c2:
                # User selects which CSV column has the new data
                val_col = st.selectbox("CSV Column with New Data", all_cols, index=0 if len(all_cols) == 0 else (1 if len(all_cols) > 1 else 0))
                
            with c3:
                # User types the actual MongoDB field key (e.g., 'phone', 'work', 'association')
                # We default this to the CSV header name for convenience
                target_field = st.text_input("Target Database Field Name", value=val_col)

            # 3. RUN UPDATE
            if st.button("🚀 Start Update Process", type="primary"):
                if not target_field:
                    st.error("⚠️ Please specify the Target Database Field Name.")
                else:
                    _process_update_logic(df, slug_col, val_col, target_field)

        except Exception as e:
            st.error(f"❌ Could not read CSV: {e}")


def _process_update_logic(df, slug_col_header, val_col_header, target_field_name):
    """
    Iterates through the DataFrame and updates the specified dynamic field in MongoDB.
    
    Args:
        df: The pandas DataFrame.
        slug_col_header: Name of the CSV column containing the Slug.
        val_col_header: Name of the CSV column containing the new value.
        target_field_name: The actual key in MongoDB to update.
    """
    
    # Initialize Counters
    stats = {
        "updated": 0,
        "skipped": 0,   # Unchanged or missing data
        "not_found": 0
    }

    # UI Elements for progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_expander = st.expander("📝 Process Logs", expanded=True)
    
    total_rows = len(df)
    logs = []

    # 4. ITERATE AND UPDATE
    for index, row in df.iterrows():
        # Update progress bar
        progress_bar.progress((index + 1) / total_rows)
        
        person_slug = row[slug_col_header]
        new_value = row[val_col_header]

        # Skip rows where data is missing
        if pd.isna(person_slug) or pd.isna(new_value):
            stats["skipped"] += 1
            continue

        person_slug = str(person_slug).strip()
        new_value = str(new_value).strip()

        status_text.text(f"Processing: {person_slug}...")

        # --- CORE DB LOGIC START ---
        # 1. Identifier: Always use 'slug' as requested
        filter_query = {"slug": person_slug}
        
        # 2. Update: Use the dynamic field name provided by user
        update_query = {
            "$set": {
                target_field_name: new_value,  # <--- Dynamic Key
                "updated_at": datetime.now()
            }
        }

        try:
            result = FAMILY_COLLECTION.update_one(filter_query, update_query)

            if result.matched_count > 0:
                if result.modified_count > 0:
                    msg = f"✅ Updated **{person_slug}**: Set `{target_field_name}` = {new_value}"
                    stats["updated"] += 1
                    logs.append(msg)
                else:
                    # msg = f"⚪ No changes needed: {person_slug}"
                    stats["skipped"] += 1
            else:
                msg = f"⚠️ Slug not found: {person_slug}"
                stats["not_found"] += 1
                logs.append(msg)

        except Exception as e:
            st.error(f"❌ Database Error on {person_slug}: {e}")
        # --- CORE DB LOGIC END ---

    # Cleanup UI
    progress_bar.empty()
    status_text.empty()

    # Show Logs
    with log_expander:
        for log in logs:
            st.markdown(log)
        if not logs:
            st.info("No major updates or errors to report.")

    # 5. SUMMARY
    st.divider()
    st.subheader("📊 Update Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Successfully Updated", stats["updated"])
    c2.metric("⚠️ Not Found", stats["not_found"])
    c3.metric("⏭️ Skipped/Unchanged", stats["skipped"])

    if stats["updated"] > 0:
        st.success(f"Batch update for field '{target_field_name}' completed successfully!")
