import mysql.connector

# MySQL DB config (same as in app.py)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

def check_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Check users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"\n===== USERS ({len(users)} records) =====")
        for user in users:
            print(f"ID: {user['id']}, Email: {user['email']}")
        
        # Check internships
        cursor.execute("SELECT * FROM internships")
        internships = cursor.fetchall()
        print(f"\n===== INTERNSHIPS ({len(internships)} records) =====")
        for internship in internships:
            print(f"ID: {internship['id']}, User ID: {internship['user_id']}, Company: {internship['company']}, Role: {internship['role']}")
        
        # Check milestones
        cursor.execute("SELECT * FROM milestones")
        milestones = cursor.fetchall()
        print(f"\n===== MILESTONES ({len(milestones)} records) =====")
        for milestone in milestones:
            print(f"ID: {milestone['id']}, User ID: {milestone['user_id']}, Title: {milestone['title']}, Date: {milestone['date']}")
        
        # Check if any internships exist with the corresponding user
        cursor.execute("""
            SELECT i.*, u.email 
            FROM internships i 
            JOIN users u ON i.user_id = u.id
        """)
        joined_data = cursor.fetchall()
        print(f"\n===== INTERNSHIPS WITH USER DATA ({len(joined_data)} records) =====")
        for item in joined_data:
            print(f"Internship ID: {item['id']}, Email: {item['email']}, Company: {item['company']}")
        
        # Check if any milestones exist with the corresponding user
        cursor.execute("""
            SELECT m.*, u.email 
            FROM milestones m 
            JOIN users u ON m.user_id = u.id
        """)
        joined_milestones = cursor.fetchall()
        print(f"\n===== MILESTONES WITH USER DATA ({len(joined_milestones)} records) =====")
        for item in joined_milestones:
            print(f"Milestone ID: {item['id']}, Email: {item['email']}, Title: {item['title']}")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return

if __name__ == "__main__":
    check_data() 