#!/usr/bin/env python3
"""
Password Migration Script for SmartCareer Database

This script migrates existing plaintext passwords in the users table
to SHA-256 hashed passwords.

Usage:
  python migrate_passwords.py

Note: Make sure your MySQL server is running before executing this script.
"""

import mysql.connector
import hashlib
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"password_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('password_migration')

# MySQL DB config (XAMPP)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

def hash_password(password):
    """Hash a password for storing"""
    if not password:
        return None
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        logger.info("Database connection established successfully")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def migrate_passwords():
    """Migrate plaintext passwords to hashed passwords"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Step 1: Get all users
        logger.info("Fetching all users from database...")
        cursor.execute("SELECT id, email, password_hash FROM users")
        users = cursor.fetchall()
        
        total_users = len(users)
        migrated_count = 0
        skipped_count = 0
        already_hashed_count = 0
        
        logger.info(f"Found {total_users} users in the database")
        
        # Step 2: Update each user with hashed password
        for user in users:
            user_id = user['id']
            email = user['email']
            current_password = user['password_hash']
            
            # Skip if password is empty or None
            if not current_password:
                logger.warning(f"User {email} (ID: {user_id}) has no password - skipping")
                skipped_count += 1
                continue
            
            # Skip if password is already hashed (64 chars = SHA-256 hash length)
            if len(current_password) == 64 and all(c in '0123456789abcdef' for c in current_password.lower()):
                logger.info(f"User {email} already has hashed password - skipping")
                already_hashed_count += 1
                continue
            
            # Hash the password
            hashed_password = hash_password(current_password)
            
            # Update the user's password
            logger.info(f"Migrating password for user {email} (ID: {user_id})")
            update_cursor = conn.cursor()
            update_cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s", 
                (hashed_password, user_id)
            )
            update_cursor.close()
            
            migrated_count += 1
        
        # Commit all changes
        conn.commit()
        
        logger.info("=" * 50)
        logger.info("Password migration completed")
        logger.info(f"Total users: {total_users}")
        logger.info(f"Users migrated: {migrated_count}")
        logger.info(f"Users already hashed: {already_hashed_count}")
        logger.info(f"Users skipped: {skipped_count}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error during password migration: {e}")
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    try:
        logger.info("Starting password migration process...")
        migrate_passwords()
        logger.info("Password migration completed successfully")
    except Exception as e:
        logger.error(f"Password migration failed: {e}")
        sys.exit(1) 