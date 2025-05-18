import mysql.connector
import sys

# MySQL DB config (same as in app.py)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

def check_connection():
    try:
        # Try connection without database first
        config_without_db = db_config.copy()
        del config_without_db['database']
        conn = mysql.connector.connect(**config_without_db)
        print("✅ Successfully connected to MySQL server")
        
        # Check if database exists
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor]
        
        if db_config['database'] in databases:
            print(f"✅ Database '{db_config['database']}' exists")
        else:
            print(f"❌ Database '{db_config['database']}' does not exist!")
            print(f"Available databases: {', '.join(databases)}")
            return
        
        # Connect to the specific database
        cursor.close()
        conn.close()
        
        # Connect with database specified
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor]
        print(f"Tables found: {', '.join(tables) if tables else 'No tables found'}")
        
        # Check if users table exists and has expected structure
        if 'users' in tables:
            cursor.execute("DESCRIBE users")
            columns = [col[0] for col in cursor.fetchall()]
            print(f"Users table columns: {', '.join(columns)}")
        else:
            print("❌ 'users' table doesn't exist!")
        
        # Check if internships table exists and has expected structure
        if 'internships' in tables:
            cursor.execute("DESCRIBE internships")
            columns = [col[0] for col in cursor.fetchall()]
            print(f"Internships table columns: {', '.join(columns)}")
        else:
            print("❌ 'internships' table doesn't exist!")
            
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return

if __name__ == "__main__":
    check_connection() 