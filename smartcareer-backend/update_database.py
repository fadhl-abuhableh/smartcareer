#!/usr/bin/env python3
"""
Database Update Script for SmartCareer

This script applies necessary database updates to support the latest version of the app.
It adds new columns to existing tables and fixes any data inconsistencies.

Usage:
  python update_database.py

Note: Make sure your MySQL server is running before executing this script.
"""

import mysql.connector
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"database_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('database_update')

# MySQL DB config (XAMPP)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartcareer_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        logger.info("Database connection established successfully")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE '{column_name}'")
    return cursor.fetchone() is not None

def update_user_profiles_table():
    """Update the user_profiles table structure"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user_profiles table exists
        if not check_table_exists(cursor, 'user_profiles'):
            logger.info("Creating user_profiles table...")
            with open('user_profiles_table.sql', 'r') as f:
                sql_commands = f.read()
                
            # Execute each command
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command)
            
            conn.commit()
            logger.info("user_profiles table created successfully")
        else:
            logger.info("user_profiles table already exists")
            
            # Check for bio column
            if not check_column_exists(cursor, 'user_profiles', 'bio'):
                logger.info("Adding bio column to user_profiles table...")
                cursor.execute("ALTER TABLE `user_profiles` ADD COLUMN `bio` text AFTER `name`")
                conn.commit()
                logger.info("bio column added successfully")
            else:
                logger.info("bio column already exists")
        
        # Sync users with profiles - create profile for any user without one
        logger.info("Syncing users with profiles...")
        cursor.execute("""
            SELECT u.email 
            FROM users u 
            LEFT JOIN user_profiles p ON u.email = p.email 
            WHERE p.email IS NULL
        """)
        
        users_without_profiles = cursor.fetchall()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for user in users_without_profiles:
            email = user[0]
            logger.info(f"Creating missing profile for user: {email}")
            cursor.execute("""
                INSERT INTO user_profiles (email, name, bio, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, "", "", current_time, current_time))
        
        if users_without_profiles:
            conn.commit()
            logger.info(f"Created {len(users_without_profiles)} missing profiles")
        else:
            logger.info("No missing profiles found")
        
    except Exception as e:
        logger.error(f"Error updating database: {e}")
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
        logger.info("Starting database update process...")
        update_user_profiles_table()
        logger.info("Database update completed successfully")
    except Exception as e:
        logger.error(f"Database update failed: {e}")
        sys.exit(1) 