import mysql.connector

# MySQL DB config (same as in app.py)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

def check_and_update_schema():
    """Check if the milestones table has a description column, and add it if it doesn't"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if description column exists in milestones table
        cursor.execute("DESCRIBE milestones")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'description' not in columns:
            print("❗ 'description' column doesn't exist in milestones table. Adding it now...")
            cursor.execute("ALTER TABLE milestones ADD COLUMN description TEXT")
            conn.commit()
            print("✅ Added 'description' column to milestones table successfully")
        else:
            print("✅ 'description' column already exists in milestones table")
        
        # Re-check structure to confirm
        cursor.execute("DESCRIBE milestones")
        columns = [col[0] for col in cursor.fetchall()]
        print(f"\nMilestones table columns: {', '.join(columns)}")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return

if __name__ == "__main__":
    check_and_update_schema() 