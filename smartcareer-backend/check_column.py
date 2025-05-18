import mysql.connector

# MySQL DB config (XAMPP)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

try:
    # Connect to database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Get the list of columns in the user_profiles table
    cursor.execute("DESCRIBE user_profiles")
    columns = cursor.fetchall()
    
    print("Columns in user_profiles table:")
    for column in columns:
        print(f"- {column[0]} ({column[1]})")
    
    # Specifically check for bio column
    cursor.execute("SHOW COLUMNS FROM user_profiles LIKE 'bio'")
    bio_column = cursor.fetchone()
    
    if bio_column:
        print("\n✅ Bio column exists!")
    else:
        print("\n❌ Bio column does not exist!")
        
        # Try to add the bio column
        print("\nAttempting to add bio column...")
        cursor.execute("ALTER TABLE user_profiles ADD COLUMN bio TEXT AFTER name")
        conn.commit()
        print("Bio column added successfully!")
    
    # Check for profile_image_url column
    cursor.execute("SHOW COLUMNS FROM user_profiles LIKE 'profile_image_url'")
    profile_image_url_column = cursor.fetchone()
    
    if profile_image_url_column:
        print("\n✅ profile_image_url column exists!")
    else:
        print("\n❌ profile_image_url column does not exist!")
        
        # Try to add the profile_image_url column
        print("\nAttempting to add profile_image_url column...")
        cursor.execute("ALTER TABLE user_profiles ADD COLUMN profile_image_url TEXT AFTER phone")
        conn.commit()
        print("profile_image_url column added successfully!")
        
except mysql.connector.Error as err:
    print(f"Database error: {err}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("\nDatabase connection closed") 