from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import os
import logging
import datetime
from werkzeug.utils import secure_filename
import hashlib
import mimetypes
import uuid

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('smartcareer')

app = Flask(__name__)

# Folder for file uploads
UPLOAD_FOLDER = 'uploads'
PROFILE_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'profile_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_IMAGES_FOLDER, exist_ok=True)

# Allowed image extensions and max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# MySQL DB config (XAMPP)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

def allowed_file(filename):
    """Check if the filename has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    """Get file size in bytes"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size

def hash_password(password):
    """Hash a password for storing"""
    # In a production environment, use a more secure hashing method with salt
    # This is a simple example using SHA-256
    return hashlib.sha256(password.encode()).hexdigest()

def save_profile_image(file):
    """Save a profile image and return the path"""
    if not file:
        logger.warning("No file provided to save_profile_image")
        return None
    
    # First check if file has a filename
    if not file.filename:
        logger.warning("File has no filename")
        return None
    
    try:
        # Check if the file extension is allowed
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file extension: {file.filename}")
            return None
        
        # Check file size
        file_size = get_file_size(file)
        if file_size > MAX_IMAGE_SIZE:
            logger.warning(f"File too large: {file.filename} ({file_size} bytes)")
            return None
        elif file_size == 0:
            logger.warning(f"Empty file: {file.filename}")
            return None
        
        # Ensure filename is safe
        original_filename = secure_filename(file.filename)
        
        # Generate a unique filename with UUID
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save the file
        file_path = os.path.join(PROFILE_IMAGES_FOLDER, unique_filename)
        file.save(file_path)
        
        # Verify the file was saved successfully
        if not os.path.exists(file_path):
            logger.error(f"Failed to save file to {file_path}")
            return None
            
        logger.info(f"File saved successfully to {file_path}")
        
        # Return the URL path for the image
        return f"/attachments/profile_images/{unique_filename}"
    except Exception as e:
        logger.error(f"Error saving profile image: {e}")
        return None

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        logger.debug("Database connection established successfully")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

@app.route("/")
def home():
    return "✅ SmartCareer API is running"

# 🔐 Register User
@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    logger.info(f"Register attempt for email: {email}")

    if not email or not password:
        logger.warning("Missing email or password in registration")
        return jsonify({"message": "Missing email or password"}), 400

    try:
        # Hash the password before storing
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        # Start transaction for data consistency
        conn.start_transaction()
        
        cursor = conn.cursor()
        
        # Insert into users table
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", 
                      (email, hashed_password))
        user_id = cursor.lastrowid
        logger.info(f"User inserted into users table: ID={user_id}, Email={email}")
        
        # Create initial profile entry
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO user_profiles (
                email, name, created_at, updated_at
            ) VALUES (%s, %s, %s, %s)
        """, (email, "", current_time, current_time))
        
        # Commit both operations
        conn.commit()
        logger.info(f"User profile initialized for: ID={user_id}, Email={email}")
        
        return jsonify({
            "message": "User registered successfully", 
            "user_id": user_id,
            "email": email
        }), 201
    
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:
            logger.warning(f"Email already registered: {email}")
            # Rollback transaction
            if 'conn' in locals() and conn.is_connected():
                conn.rollback()
            return jsonify({"message": "Email already registered"}), 409
        logger.error(f"Database error during registration: {e}")
        # Rollback transaction
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({"message": "Database error", "error": str(e)}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        # Rollback transaction
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# 🔐 Login User
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    logger.info(f"Login attempt for email: {email}")

    if not email or not password:
        logger.warning("Missing credentials in login")
        return jsonify({"message": "Missing credentials"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First try with the hashed password (for users created after the update)
        hashed_password = hash_password(password)
        cursor.execute("SELECT id, email FROM users WHERE email = %s AND password_hash = %s", 
                      (email, hashed_password))
        user = cursor.fetchone()
        
        # If no user found, try with unhashed password (for existing users)
        if not user:
            logger.info(f"Trying legacy password authentication for {email}")
            cursor.execute("SELECT id, email FROM users WHERE email = %s AND password_hash = %s", 
                          (email, password))
            user = cursor.fetchone()
            
            # If user found with unhashed password, update to hashed for future logins
        if user:
                logger.info(f"Migrating user {email} to hashed password")
                cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", 
                              (hashed_password, email))
                conn.commit()
        
        if user:
            user_id = user['id']
            logger.info(f"Login successful: ID={user_id}, Email={email}")
            
            # Fetch the user's profile if it exists
            cursor.execute("""
                SELECT name
                FROM user_profiles
                WHERE email = %s
            """, (email,))
            
            profile = cursor.fetchone()
            
            response = {
                "message": "Login successful", 
                "user_id": user_id, 
                "email": email
            }
            
            # Add profile data if available
            if profile:
                response["name"] = profile["name"] if profile["name"] else ""
            
            return jsonify(response)
        else:
            logger.warning(f"Invalid credentials for email: {email}")
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 📄 Add Internship
@app.route('/add_internship', methods=['POST'])
def add_internship():
    email = request.form.get('email')
    logger.info(f"Add internship attempt for email: {email}")
    
    if not email:
        logger.warning("Missing email in add_internship")
        return jsonify({"message": "Missing email"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404

        user_id = result[0]
        company = request.form.get('company')
        role = request.form.get('role')
        dates = request.form.get('dates')
        description = request.form.get('description')
        file = request.files.get('attachment')

        logger.info(f"Internship data: user_id={user_id}, company={company}, role={role}, dates={dates}")

        if not all([company, role, dates, description]):
            logger.warning("Missing required fields in add_internship")
            return jsonify({"message": "Missing one or more required fields"}), 400

        filename = None
        if file:
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            logger.info(f"File saved: {filename}")

        logger.debug(f"Executing SQL INSERT for internship: user_id={user_id}, company={company}")
        cursor.execute("""
            INSERT INTO internships (user_id, company, role, dates, description, filename)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, company, role, dates, description, filename))
        
        conn.commit()
        internship_id = cursor.lastrowid
        logger.info(f"Internship added successfully: ID={internship_id}, User ID={user_id}")
        
        # Verify the insertion worked by querying the database
        cursor.execute("SELECT * FROM internships WHERE id = %s", (internship_id,))
        verification = cursor.fetchone()
        if verification:
            logger.info(f"Verified insertion: record found with ID={internship_id}")
        else:
            logger.warning(f"Verification failed: no record found with ID={internship_id}")
            
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Internship submitted successfully", 
            "internship_id": internship_id,
            "verification": "OK" if verification else "Failed"
        }), 201
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in add_internship: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in add_internship: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 🏆 Add Milestone
@app.route('/add_milestone', methods=['POST'])
def add_milestone():
    email = request.form.get('email')
    logger.info(f"Add milestone attempt for email: {email}")
    
    if not email:
        logger.warning("Missing email in add_milestone")
        return jsonify({"message": "Missing email"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404

        user_id = result[0]
        title = request.form.get('title')
        date = request.form.get('date')
        description = request.form.get('description', '')
        file = request.files.get('attachment')

        logger.info(f"Milestone data: user_id={user_id}, title={title}, date={date}, description={description}")

        if not all([title, date]):
            logger.warning("Missing title or date in add_milestone")
            return jsonify({"message": "Missing title or date"}), 400

        filename = None
        if file:
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            logger.info(f"File saved: {filename}")

        logger.debug(f"Executing SQL INSERT for milestone: user_id={user_id}, title={title}")
        cursor.execute("""
            INSERT INTO milestones (user_id, title, date, description, filename)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, title, date, description, filename))
        
        conn.commit()
        milestone_id = cursor.lastrowid
        logger.info(f"Milestone added successfully: ID={milestone_id}, User ID={user_id}")
        
        # Verify the insertion worked by querying the database
        cursor.execute("SELECT * FROM milestones WHERE id = %s", (milestone_id,))
        verification = cursor.fetchone()
        if verification:
            logger.info(f"Verified milestone insertion: record found with ID={milestone_id}")
        else:
            logger.warning(f"Verification failed: no milestone record found with ID={milestone_id}")
        
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Milestone added successfully", 
            "milestone_id": milestone_id,
            "verification": "OK" if verification else "Failed"
        }), 201
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in add_milestone: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in add_milestone: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 🧠 AI Resume Feedback
@app.route('/api/resume-feedback', methods=['POST'])
def api_resume_feedback():
    try:
        # Get JSON data from request
        user_data = request.get_json()
        logger.info(f"Resume feedback request received for email: {user_data.get('email')}")
        
        if not user_data:
            logger.warning("No data provided in resume feedback request")
            return jsonify({"message": "No data provided"}), 400
        
        # If no email is provided, return an error
        if 'email' not in user_data:
            logger.warning("No email provided in resume feedback request")
            return jsonify({"message": "Email is required"}), 400
            
        # Get user data from database if not provided in request
        if 'internships' not in user_data or not user_data['internships']:
            user_data['internships'] = get_user_internships(user_data['email'])
            logger.info(f"Retrieved {len(user_data['internships'])} internships from database")
            
        if 'milestones' not in user_data or not user_data['milestones']:
            user_data['milestones'] = get_user_milestones(user_data['email'])
            logger.info(f"Retrieved {len(user_data['milestones'])} milestones from database")
        
        # If skills are not provided, add an empty list
        if 'skills' not in user_data:
            user_data['skills'] = []
        
        # Import the AI service here to avoid circular imports
        import ai_service_gemini
        
        # Generate the feedback
        feedback = ai_service_gemini.generate_resume_feedback(user_data)
        logger.info(f"Resume feedback generated successfully for {user_data.get('email')}")
        
        return jsonify(feedback)
        
    except Exception as e:
        logger.error(f"Error in resume feedback endpoint: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 💡 AI Career Advice
@app.route('/api/career-advice', methods=['POST'])
def api_career_advice():
    try:
        # Get JSON data from request
        user_data = request.get_json()
        logger.info(f"Career advice request received for email: {user_data.get('email')}")
        
        if not user_data:
            logger.warning("No data provided in career advice request")
            return jsonify({"message": "No data provided"}), 400
        
        # If no email is provided, return an error
        if 'email' not in user_data:
            logger.warning("No email provided in career advice request")
            return jsonify({"message": "Email is required"}), 400
            
        # Get user data from database if not provided in request
        if 'internships' not in user_data or not user_data['internships']:
            user_data['internships'] = get_user_internships(user_data['email'])
            logger.info(f"Retrieved {len(user_data['internships'])} internships from database")
            
        if 'milestones' not in user_data or not user_data['milestones']:
            user_data['milestones'] = get_user_milestones(user_data['email'])
            logger.info(f"Retrieved {len(user_data['milestones'])} milestones from database")
        
        # If skills are not provided, add an empty list
        if 'skills' not in user_data:
            user_data['skills'] = []
        
        # Import the AI service here to avoid circular imports
        import ai_service_gemini
        
        # Generate the career advice
        advice = ai_service_gemini.generate_career_advice(user_data)
        logger.info(f"Career advice generated successfully for {user_data.get('email')}")
        
        return jsonify(advice)
        
    except Exception as e:
        logger.error(f"Error in career advice endpoint: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 🗺️ AI Detailed Roadmap
@app.route('/api/detailed-roadmap', methods=['POST'])
def api_detailed_roadmap():
    try:
        # Get JSON data from request
        user_data = request.get_json()
        logger.info(f"Detailed roadmap request received for email: {user_data.get('email')}")
        
        if not user_data:
            logger.warning("No data provided in detailed roadmap request")
            return jsonify({"message": "No data provided"}), 400
        
        # If no email is provided, return an error
        if 'email' not in user_data:
            logger.warning("No email provided in detailed roadmap request")
            return jsonify({"message": "Email is required"}), 400
            
        # Get user data from database if not provided in request
        if 'internships' not in user_data or not user_data['internships']:
            user_data['internships'] = get_user_internships(user_data['email'])
            logger.info(f"Retrieved {len(user_data['internships'])} internships from database")
            
        if 'milestones' not in user_data or not user_data['milestones']:
            user_data['milestones'] = get_user_milestones(user_data['email'])
            logger.info(f"Retrieved {len(user_data['milestones'])} milestones from database")
        
        # If skills are not provided, add an empty list
        if 'skills' not in user_data:
            user_data['skills'] = []
        
        # Import the AI service here to avoid circular imports
        import ai_service_gemini
        
        # Generate the detailed roadmap
        roadmap = ai_service_gemini.generate_detailed_roadmap(user_data)
        logger.info(f"Detailed roadmap generated successfully for {user_data.get('email')}")
        
        return jsonify(roadmap)
        
    except Exception as e:
        logger.error(f"Error in detailed roadmap endpoint: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# Helper function to get user internships from database
def get_user_internships(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First get the user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return []
        
        user_id = user_result['id']
        
        # Get all internships for this user
        cursor.execute("""
            SELECT id, company, role, dates, description, filename
            FROM internships
            WHERE user_id = %s
        """, (user_id,))
        
        internships = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert IDs to strings for JSON serialization
        for internship in internships:
            if 'id' in internship:
                internship['id'] = str(internship['id'])
        
        return internships
        
    except Exception as e:
        logger.error(f"Error retrieving internships from database: {e}")
        return []

# Helper function to get user milestones from database
def get_user_milestones(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First get the user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return []
        
        user_id = user_result['id']
        
        # Get all milestones for this user
        cursor.execute("""
            SELECT id, title, date, description, filename
            FROM milestones
            WHERE user_id = %s
        """, (user_id,))
        
        milestones = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert IDs to strings and format dates for JSON serialization
        for milestone in milestones:
            if 'id' in milestone:
                milestone['id'] = str(milestone['id'])
            if 'date' in milestone and hasattr(milestone['date'], 'strftime'):
                milestone['date'] = milestone['date'].strftime('%Y-%m-%d')
        
        return milestones
        
    except Exception as e:
        logger.error(f"Error retrieving milestones from database: {e}")
        return []

# 📄 Get Internships for a User
@app.route('/get_internships', methods=['GET'])
def get_internships():
    email = request.args.get('email')
    logger.info(f"Get internships request for email: {email}")
    
    if not email:
        logger.warning("Missing email in get_internships request")
        return jsonify({"message": "Missing email parameter"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First get the user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404
        
        user_id = user_result['id']
        logger.info(f"Found user with ID: {user_id}")
        
        # Now get all internships for this user
        cursor.execute("""
            SELECT i.id, i.company, i.role, i.dates, i.description, i.filename
            FROM internships i
            WHERE i.user_id = %s
            ORDER BY i.id DESC
        """, (user_id,))
        
        internships = cursor.fetchall()
        logger.info(f"Found {len(internships)} internships for user {email}")
        
        # Convert to proper format for Android client
        internship_list = []
        for internship in internships:
            item = {
                "id": str(internship['id']),
                "company": internship['company'],
                "role": internship['role'],
                "dates": internship['dates'],
                "description": internship['description'],
                "filename": internship['filename'] if internship['filename'] else ""
            }
            internship_list.append(item)
        
        cursor.close()
        conn.close()
        
        return jsonify(internship_list)
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in get_internships: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_internships: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 🏆 Get Milestones for a User
@app.route('/get_milestones', methods=['GET'])
def get_milestones():
    email = request.args.get('email')
    logger.info(f"Get milestones request for email: {email}")
    
    if not email:
        logger.warning("Missing email in get_milestones request")
        return jsonify({"message": "Missing email parameter"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First get the user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404
        
        user_id = user_result['id']
        logger.info(f"Found user with ID: {user_id}")
        
        # Now get all milestones for this user
        cursor.execute("""
            SELECT m.id, m.title, m.date, m.description, m.filename
            FROM milestones m
            WHERE m.user_id = %s
            ORDER BY m.date DESC
        """, (user_id,))
        
        milestones = cursor.fetchall()
        logger.info(f"Found {len(milestones)} milestones for user {email}")
        
        # Convert to proper format for Android client
        milestone_list = []
        for milestone in milestones:
            item = {
                "id": str(milestone['id']),
                "title": milestone['title'],
                "date": milestone['date'].strftime('%Y-%m-%d') if hasattr(milestone['date'], 'strftime') else milestone['date'],
                "description": milestone['description'] if milestone['description'] else "",
                "filename": milestone['filename'] if milestone['filename'] else ""
            }
            milestone_list.append(item)
        
        cursor.close()
        conn.close()
        
        return jsonify(milestone_list)
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in get_milestones: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_milestones: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 🗑️ Delete Internship
@app.route('/delete_internship', methods=['POST'])
def delete_internship():
    email = request.form.get('email')
    internship_id = request.form.get('id')
    logger.info(f"Delete internship request for email: {email}, internship ID: {internship_id}")
    
    if not email or not internship_id:
        logger.warning("Missing email or internship ID in delete_internship request")
        return jsonify({"message": "Missing email or internship ID"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First get the user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404
        
        user_id = user_result[0]
        
        # Delete the internship only if it belongs to this user (security check)
        cursor.execute("""
            DELETE FROM internships 
            WHERE id = %s AND user_id = %s
        """, (internship_id, user_id))
        
        if cursor.rowcount == 0:
            logger.warning(f"Internship not found or does not belong to user: internship_id={internship_id}, user_id={user_id}")
            cursor.close()
            conn.close()
            return jsonify({"message": "Internship not found or access denied"}), 404
        
        conn.commit()
        logger.info(f"Internship deleted successfully: ID={internship_id}")
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Internship deleted successfully"})
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in delete_internship: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in delete_internship: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 🗑️ Delete Milestone
@app.route('/delete_milestone', methods=['POST'])
def delete_milestone():
    email = request.form.get('email')
    milestone_id = request.form.get('id')
    logger.info(f"Delete milestone request for email: {email}, milestone ID: {milestone_id}")
    
    if not email or not milestone_id:
        logger.warning("Missing email or milestone ID in delete_milestone request")
        return jsonify({"message": "Missing email or milestone ID"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First get the user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found"}), 404
        
        user_id = user_result[0]
        
        # Delete the milestone only if it belongs to this user (security check)
        cursor.execute("""
            DELETE FROM milestones 
            WHERE id = %s AND user_id = %s
        """, (milestone_id, user_id))
        
        if cursor.rowcount == 0:
            logger.warning(f"Milestone not found or does not belong to user: milestone_id={milestone_id}, user_id={user_id}")
            cursor.close()
            conn.close()
            return jsonify({"message": "Milestone not found or access denied"}), 404
        
        conn.commit()
        logger.info(f"Milestone deleted successfully: ID={milestone_id}")
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Milestone deleted successfully"})
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in delete_milestone: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in delete_milestone: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

# 📎 Serve attachment files
@app.route('/attachments/<path:filename>')
def serve_attachment(filename):
    # If it's a profile image
    if filename.startswith('profile_images/'):
        # Split the path into directory and filename
        directory, image_filename = os.path.split(filename)
        logger.info(f"Serving profile image: {image_filename}")
        return send_from_directory(PROFILE_IMAGES_FOLDER, image_filename)
    else:
        # Regular attachment
        logger.info(f"Serving attachment: {filename}")
        return send_from_directory(UPLOAD_FOLDER, filename)

# 🧠 AI Resume Feedback - Alias for backward compatibility
@app.route('/get_resume_feedback', methods=['POST'])
def get_resume_feedback_alias():
    logger.info("Resume feedback request received through legacy endpoint")
    return api_resume_feedback()

# 💡 AI Career Advice - Alias for backward compatibility
@app.route('/get_career_advice', methods=['POST'])
def get_career_advice_alias():
    logger.info("Career advice request received through legacy endpoint")
    return api_career_advice()

# 🗺️ AI Detailed Roadmap - Alias for backward compatibility
@app.route('/get_detailed_roadmap', methods=['POST'])
def get_detailed_roadmap_alias():
    logger.info("Detailed roadmap request received through legacy endpoint")
    return api_detailed_roadmap()

# 👤 Get User Profile
@app.route('/api/user-profile', methods=['GET'])
def get_user_profile():
    email = request.args.get('email')
    logger.info(f"Get user profile request for email: {email}")
    logger.debug(f"Profile request headers: {dict(request.headers)}")
    logger.debug(f"Profile request args: {dict(request.args)}")
    
    if not email:
        logger.warning("Missing email in get_user_profile request")
        return jsonify({"message": "Missing email parameter", "success": False}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First check if user exists in the users table
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"User not found for email: {email}")
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found", "success": False}), 404
        
        user_id = user_result['id']
        
        # Check if profile exists in user_profiles table
        cursor.execute("""
            SELECT id, email, name, bio, birthday, phone, created_at, updated_at
            FROM user_profiles
            WHERE email = %s
        """, (email,))
        
        profile = cursor.fetchone()
        
        if not profile:
            # Profile doesn't exist yet, create a basic one
            logger.info(f"Profile not found for user {email}, creating basic profile")
            
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert a basic profile
            cursor.execute("""
                INSERT INTO user_profiles (email, name, bio, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, "", "", current_time, current_time))
            
            conn.commit()
            
            # Retrieve the newly created profile
            cursor.execute("""
                SELECT id, email, name, bio, birthday, phone, created_at, updated_at
                FROM user_profiles
                WHERE email = %s
            """, (email,))
            
            profile = cursor.fetchone()
            
            if not profile:
                logger.error(f"Failed to create basic profile for {email}")
                return jsonify({
                    "message": "Failed to create user profile", 
                    "success": False
                }), 500
        
        # Format date fields for JSON serialization
        if profile['birthday'] and hasattr(profile['birthday'], 'strftime'):
            profile['birthday'] = profile['birthday'].strftime('%Y-%m-%d')
        if profile['created_at'] and hasattr(profile['created_at'], 'strftime'):
            profile['created_at'] = profile['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if profile['updated_at'] and hasattr(profile['updated_at'], 'strftime'):
            profile['updated_at'] = profile['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Add success flag
        profile['success'] = True
        
        # Debug logging to help diagnose client issues
        logger.debug(f"Response data (full profile): {profile}")
        logger.info(f"Profile retrieved successfully for user {email}")
        cursor.close()
        conn.close()
        
        return jsonify(profile)
    
    except mysql.connector.Error as err:
        logger.error(f"Database error in get_user_profile: {err}")
        return jsonify({"message": "Database error", "error": str(err), "success": False}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_user_profile: {e}")
        return jsonify({"message": "Server error", "error": str(e), "success": False}), 500

# 📧 Change Email
@app.route('/api/change-email', methods=['POST'])
def change_email():
    try:
        # Get data from either JSON or form data
        data = request.get_json(silent=True) or request.form
        
        current_email = data.get('current_email')
        new_email = data.get('new_email')
        password = data.get('password')  # Require password for security
        
        logger.info(f"Email change request for: {current_email} -> {new_email}")
        
        if not all([current_email, new_email, password]):
            logger.warning("Missing required fields in change_email request")
            return jsonify({
                "message": "Missing required fields: current_email, new_email, and password",
                "success": False
            }), 400
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Start transaction
            conn.start_transaction()
            
            # Verify current password
            hashed_password = hash_password(password)
            cursor.execute("""
                SELECT id FROM users 
                WHERE email = %s AND password_hash = %s
            """, (current_email, hashed_password))
            
            user = cursor.fetchone()
            if not user:
                logger.warning(f"Password verification failed for {current_email}")
                conn.rollback()
                return jsonify({
                    "message": "Current password is incorrect",
                    "success": False
                }), 401
            
            # Check if new email is already in use
            cursor.execute("SELECT id FROM users WHERE email = %s", (new_email,))
            if cursor.fetchone():
                logger.warning(f"New email {new_email} is already in use")
                conn.rollback()
                return jsonify({
                    "message": "New email is already in use",
                    "success": False
                }), 409
            
            # Update email in users table
            cursor.execute("""
                UPDATE users 
                SET email = %s
                WHERE email = %s
            """, (new_email, current_email))
            
            if cursor.rowcount == 0:
                logger.error(f"Failed to update email in users table")
                conn.rollback()
                return jsonify({
                    "message": "Failed to update email",
                    "success": False
                }), 500
            
            # Update email in user_profiles table
            cursor.execute("""
                UPDATE user_profiles 
                SET email = %s
                WHERE email = %s
            """, (new_email, current_email))
            
            if cursor.rowcount == 0:
                logger.error(f"Failed to update email in user_profiles table")
                conn.rollback()
                return jsonify({
                    "message": "Failed to update email",
                    "success": False
                }), 500
            
            # Commit transaction
            conn.commit()
            logger.info(f"Email updated successfully from {current_email} to {new_email}")
            
            return jsonify({
                "message": "Email updated successfully",
                "new_email": new_email,
                "success": True
            })
            
        except mysql.connector.Error as err:
            logger.error(f"Database error in change_email: {err}")
            if conn and conn.is_connected():
                conn.rollback()
            return jsonify({"message": "Database error", "error": str(err), "success": False}), 500
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                
    except Exception as e:
        logger.error(f"Unexpected error in change_email: {e}")
        return jsonify({"message": "Server error", "error": str(e), "success": False}), 500

# Modify update_profile to remove email change functionality
@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    try:
        # Log incoming request data
        request_data = {
            "form": dict(request.form),
            "headers": {key: value for key, value in request.headers.items() if key.lower() not in ['authorization', 'cookie']}
        }
        logger.debug(f"Raw update_profile request data: {request_data}")
        
        # Get form data
        data = request.form
        
        # Get email for user identification
        email = data.get('current_email')
        if not email:
            logger.warning("Missing current_email in update_profile request")
            return jsonify({
                "message": "Missing required parameter: current_email",
                "success": False
            }), 400
        
        try:
            # Get optional fields
            name = data.get('name')
            bio = data.get('bio')
            birthday = data.get('birthday')
            phone = data.get('phone')
            
            # Log the parsed data
            parsed_data = {
                "email": email,
                "name": name,
                "bio": bio,
                "birthday": birthday,
                "phone": phone
            }
            logger.debug(f"Parsed update_profile data: {parsed_data}")
            
            # Validate birthday format if provided
            if birthday:
                try:
                    datetime.datetime.strptime(birthday, '%Y-%m-%d')
                except ValueError:
                    error_msg = f"Invalid birthday format: {birthday}. Use YYYY-MM-DD format."
                    logger.warning(error_msg)
                    return jsonify({
                        "message": error_msg,
                        "success": False
                    }), 400
            
            # Database operations
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                # First check if user exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user_result = cursor.fetchone()
                
                if not user_result:
                    logger.warning(f"User not found for email: {email}")
                    return jsonify({
                        "message": "User not found",
                        "success": False
                    }), 404
                
                # Get current profile data
                cursor.execute("""
                    SELECT id, email, name, bio, birthday, phone, profile_image_url, created_at, updated_at
                    FROM user_profiles
                    WHERE email = %s
                """, (email,))
                
                current_profile = cursor.fetchone()
                
                if not current_profile:
                    # Create new profile with provided data
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    insert_query = """
                        INSERT INTO user_profiles (
                            email, name, bio, birthday, phone, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    insert_params = (
                        email,
                        name or "",
                        bio or "",
                        birthday,
                        phone or "",
                        current_time,
                        current_time
                    )
                    
                    logger.debug(f"Executing INSERT query: {insert_query} with params: {insert_params}")
                    cursor.execute(insert_query, insert_params)
                    
                    if cursor.rowcount == 0:
                        logger.error(f"Failed to create profile for {email}")
                        return jsonify({
                            "message": "Failed to create profile",
                            "success": False
                        }), 500
                    
                    logger.info(f"New profile created for user {email}")
                else:
                    # Build dynamic update query based on provided fields
                    update_fields = []
                    params = []
                    
                    if name is not None:
                        update_fields.append("name = %s")
                        params.append(name)
                    
                    if bio is not None:
                        update_fields.append("bio = %s")
                        params.append(bio)
                    
                    if birthday is not None:
                        update_fields.append("birthday = %s")
                        params.append(birthday)
                    
                    if phone is not None:
                        update_fields.append("phone = %s")
                        params.append(phone)
                    
                    if update_fields:
                        update_fields.append("updated_at = %s")
                        params.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        params.append(email)  # For WHERE clause
                        
                        update_query = f"""
                            UPDATE user_profiles 
                            SET {', '.join(update_fields)}
                            WHERE email = %s
                        """
                        
                        logger.debug(f"Executing UPDATE query: {update_query} with params: {params}")
                        cursor.execute(update_query, params)
                        
                        if cursor.rowcount == 0:
                            logger.warning(f"Profile update had no effect for {email}")
                        else:
                            logger.info(f"Profile updated for user {email}")
                        
                        # Commit the changes
                        conn.commit()
                        logger.debug("Database changes committed successfully")
                
                # Get the updated profile
                cursor.execute("""
                    SELECT id, email, name, bio, birthday, phone, profile_image_url, created_at, updated_at
                    FROM user_profiles
                    WHERE email = %s
                """, (email,))
                
                updated_profile = cursor.fetchone()
                
                if not updated_profile:
                    logger.error(f"Failed to retrieve updated profile for {email}")
                    return jsonify({
                        "message": "Failed to retrieve updated profile",
                        "success": False
                    }), 500
                
                # Format date fields for JSON serialization
                if updated_profile['birthday'] and hasattr(updated_profile['birthday'], 'strftime'):
                    updated_profile['birthday'] = updated_profile['birthday'].strftime('%Y-%m-%d')
                if updated_profile['created_at'] and hasattr(updated_profile['created_at'], 'strftime'):
                    updated_profile['created_at'] = updated_profile['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if updated_profile['updated_at'] and hasattr(updated_profile['updated_at'], 'strftime'):
                    updated_profile['updated_at'] = updated_profile['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                # Prepare response data
                response_data = {
                    "name": updated_profile['name'] or "",
                    "bio": updated_profile['bio'] or "",
                    "phone": updated_profile['phone'] or "",
                    "birthday": updated_profile['birthday'] or "",
                    "email": updated_profile['email'],
                    "profile_image_url": updated_profile['profile_image_url'] or "",
                    "success": True
                }
                
                logger.debug(f"Response data: {response_data}")
                return jsonify(response_data)
                
            except mysql.connector.Error as err:
                logger.error(f"Database error in update_profile: {err}")
                if conn and conn.is_connected():
                    conn.rollback()
                return jsonify({
                    "message": "Database error",
                    "error": str(err),
                    "success": False
                }), 500
            finally:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
                    
        except Exception as e:
            logger.error(f"Error parsing request data: {e}")
            return jsonify({
                "message": "Error processing request data",
                "error": str(e),
                "success": False
            }), 400
    
    except Exception as e:
        logger.error(f"Unexpected error in update_profile: {e}")
        return jsonify({
            "message": "Server error",
            "error": str(e),
            "success": False
        }), 500

# 🛠️ Debug Profile API
@app.route('/api/debug-profile', methods=['GET'])
def debug_profile():
    """Debug endpoint to test profile API without database interaction"""
    email = request.args.get('email', 'test@example.com')
    logger.info(f"Debug profile request for email: {email}")
    
    # Return a sample profile that matches the expected structure
    sample_profile = {
        "id": 999,
        "email": email,
        "name": "Test User",
        "birthday": "1990-01-01",
        "phone": "+1234567890",
        "profile_image_url": None,
        "created_at": "2025-05-16 12:34:56",
        "updated_at": "2025-05-16 12:34:56",
        "exists": True,
        "debug_info": {
            "request_headers": dict(request.headers),
            "request_args": dict(request.args),
            "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    # Log the response for debugging
    logger.debug(f"Debug profile response: {sample_profile}")
    
    # Return the sample profile
    return jsonify(sample_profile)

# 🔑 Change Password
@app.route('/change-password', methods=['POST'])
def change_password():
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    logger.info(f"Password change request for email: {email}")
    
    # Validate inputs
    if not all([email, current_password, new_password]):
        logger.warning("Missing required fields in change_password request")
        return jsonify({"message": "Missing required fields", "success": False}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Start transaction
        conn.start_transaction()
        
        # First verify the current password
        current_hashed = hash_password(current_password)
        cursor.execute("""
            SELECT id FROM users 
            WHERE email = %s AND (password_hash = %s OR password_hash = %s)
        """, (email, current_hashed, current_password))
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"Current password verification failed for {email}")
            conn.rollback()
            return jsonify({"message": "Current password is incorrect", "success": False}), 401
        
        # Hash the new password
        new_hashed = hash_password(new_password)
        
        # Update the password in the database
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s
            WHERE email = %s
        """, (new_hashed, email))
        
        # Check if the update was successful
        if cursor.rowcount == 0:
            logger.error(f"No rows affected when updating password for {email}")
            conn.rollback()
            return jsonify({"message": "Failed to update password", "success": False}), 500
        
        # Commit the transaction
        conn.commit()
        
        logger.info(f"Password updated successfully for {email}")
        return jsonify({"message": "Password updated successfully", "success": True})
        
    except mysql.connector.Error as err:
        logger.error(f"Database error in change_password: {err}")
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({"message": "Database error", "error": str(err), "success": False}), 500
    except Exception as e:
        logger.error(f"Unexpected error in change_password: {e}")
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e), "success": False}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# 🧪 Test Form Upload
@app.route('/api/test-form-upload', methods=['POST'])
def test_form_upload():
    """Test endpoint for diagnosing form upload issues"""
    try:
        response_data = {
            "success": True,
            "message": "Form data received successfully",
            "form_data": {k: v for k, v in request.form.items()},
            "files": [],
            "headers": {k: v for k, v in request.headers.items() 
                      if k.lower() not in ['authorization', 'cookie']}
        }
        
        # Process any files
        if request.files:
            for file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    response_data["files"].append({
                        "name": file_key,
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "size": get_file_size(file)
                    })
                else:
                    response_data["files"].append({
                        "name": file_key,
                        "error": "No filename or empty file"
                    })
        
        logger.info(f"Test form upload received: {len(response_data['form_data'])} form fields, {len(response_data['files'])} files")
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in test_form_upload: {e}")
        return jsonify({
            "success": False,
            "message": "Error processing form data",
            "error": str(e)
        }), 500

# 🧪 API Connection Test
@app.route('/api/test-connection', methods=['GET', 'POST'])
def test_connection():
    """Simple endpoint to test API connectivity from the app"""
    response_data = {
        "success": True,
        "message": "API connection successful",
        "method": request.method,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "headers": {k: v for k, v in request.headers.items() if k.lower() not in ['authorization', 'cookie']}
    }
    
    # If it's a GET request, include the query parameters
    if request.method == 'GET':
        response_data["params"] = dict(request.args)
    
    # If it's a POST request, include the form data
    if request.method == 'POST':
        response_data["form_data"] = dict(request.form)
        response_data["has_files"] = len(request.files) > 0
    
    logger.info(f"Connection test hit: {request.method} request from {request.remote_addr}")
    return jsonify(response_data)

# 👤 User Profile Endpoints - URL Aliases without /api/ prefix
@app.route('/user-profile', methods=['GET'])
def get_user_profile_alias():
    """Alias for the /api/user-profile endpoint"""
    logger.info("Request received at /user-profile alias")
    return get_user_profile()

@app.route('/update-profile', methods=['POST'])
def update_profile_alias():
    """Alias for the /api/update-profile endpoint"""
    logger.info("Request received at /update-profile alias")
    return update_profile()

# 👤 Update Profile Image
@app.route('/api/update-profile-image', methods=['POST'])
def update_profile_image():
    try:
        # Get email from form data
        email = request.form.get('email')
        logger.info(f"Update profile image request for email: {email}")
        
        if not email:
            logger.warning("Missing email in update_profile_image request")
            return jsonify({"message": "Missing email parameter", "success": False}), 400
        
        # Get the image file
        if 'profileImage' not in request.files:
            logger.warning("No profile image file in request")
            return jsonify({"message": "No profile image provided", "success": False}), 400
        
        file = request.files['profileImage']
        if not file or not file.filename:
            logger.warning("Empty profile image file")
            return jsonify({"message": "Empty profile image file", "success": False}), 400
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Start transaction
            conn.start_transaction()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_result = cursor.fetchone()
            
            if not user_result:
                logger.warning(f"User not found for email: {email}")
                conn.rollback()
                return jsonify({"message": "User not found", "success": False}), 404
            
            # Save the profile image
            image_url = save_profile_image(file)
            if not image_url:
                logger.error("Failed to save profile image")
                conn.rollback()
                return jsonify({"message": "Failed to save profile image", "success": False}), 500
            
            # Update the profile with the new image URL
            cursor.execute("""
                UPDATE user_profiles 
                SET profile_image_url = %s,
                    updated_at = %s
                WHERE email = %s
            """, (image_url, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email))
            
            if cursor.rowcount == 0:
                logger.warning(f"No profile found to update for {email}")
                conn.rollback()
                return jsonify({"message": "Profile not found", "success": False}), 404
            
            # Commit the transaction
            conn.commit()
            logger.info(f"Profile image updated successfully for {email}")
            
            return jsonify({
                "message": "Profile image updated successfully",
                "profile_image_url": image_url,
                "success": True
            })
            
        except mysql.connector.Error as err:
            logger.error(f"Database error in update_profile_image: {err}")
            if conn and conn.is_connected():
                conn.rollback()
            return jsonify({"message": "Database error", "error": str(err), "success": False}), 500
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                
    except Exception as e:
        logger.error(f"Unexpected error in update_profile_image: {e}")
        return jsonify({"message": "Server error", "error": str(e), "success": False}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
