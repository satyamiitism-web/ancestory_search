from datetime import datetime
from database import FAMILY_COLLECTION
import pandas as pd



def run_update_script(csv_file_path):

    print(f"📂 Reading CSV file: {csv_file_path}...")
    try:
        df = pd.read_csv(csv_file_path)
        # Ensure column names are clean (strip spaces)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"❌ Could not read CSV: {e}")
        return

    # 3. DEFINE COLUMN MAPPING
    # ------------------------
    # Change these to match your CSV headers exactly
    NAME_COL = "name"              # Column in CSV identifying the person
    UPDATE_COL = "association"     # Column in CSV with the new value (suggestion value)

    # Check if columns exist
    if NAME_COL not in df.columns or UPDATE_COL not in df.columns:
        print(f"❌ Error: CSV must contain columns '{NAME_COL}' and '{UPDATE_COL}'")
        print(f"Found columns: {df.columns.tolist()}")
        return

    # 4. ITERATE AND UPDATE
    # ---------------------
    count_updated = 0
    count_skipped = 0
    count_not_found = 0

    print("🔄 Starting update process...")

    for index, row in df.iterrows():
        person_name = row[NAME_COL]
        new_value = row[UPDATE_COL]

        # Skip rows where data is missing
        if pd.isna(person_name) or pd.isna(new_value):
            count_skipped += 1
            continue

        person_name = str(person_name).strip()
        new_value = str(new_value).strip()

        # FIND the person in DB
        # We assume 'name' is unique. If you use 'slug', change query to {"slug": person_name.lower()}
        filter_query = {"name": person_name} 
        
        # UPDATE operation
        # We set the 'association' field to the value from CSV
        update_query = {
            "$set": {
                "association": new_value,
                "updated_at": pd.Timestamp.now() # Optional: Audit trail
            }
        }

        result = FAMILY_COLLECTION.update_one(filter_query, update_query)

        if result.matched_count > 0:
            if result.modified_count > 0:
                print(f"   ✅ Updated: {person_name} -> {new_value}")
                count_updated += 1
            else:
                print(f"   aaa No changes needed: {person_name}")
                count_skipped += 1
        else:
            print(f"   ⚠️ Person not found: {person_name}")
            count_not_found += 1

    # 5. SUMMARY
    # ----------
    print("\n" + "="*30)
    print("📊 UPDATE SUMMARY")
    print("="*30)
    print(f"✅ Successfully Updated: {count_updated}")
    print(f"⚠️ Not Found in DB:      {count_not_found}")
    print(f"⏭️ Skipped/Unchanged:    {count_skipped}")
    print("="*30)

if __name__ == "__main__":
    # Replace with your actual CSV filename
    run_update_script(r"C:\Users\satya\Downloads\2026-01-01T03-10_export.csv")
