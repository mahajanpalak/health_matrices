# database.py
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import hashlib
import os
import json

def get_db_path():
    """
    Get database path that works in both local and deployed environments
    Uses a fixed database file name that gets committed to Git
    """
    return 'health_app_persistent.db'

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    """Verify a stored password against one provided by user"""
    return hash_password(plain_password) == hashed_password

def init_db():
    """Initialize the database and create tables"""
    db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User profiles table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            gender TEXT,
            goal TEXT,
            diet_preference TEXT,
            allergies TEXT,
            injuries TEXT,
            lifestyle TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, password, email=""):
    """Create a new user with hashed password"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        # Hash the password before storing
        hashed_password = hash_password(password)
        
        c.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_password, email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials with hashed password"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Get the stored hashed password
        c.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,)
        )
        user = c.fetchone()
        
        if user:
            user_id, username, stored_hashed_password = user
            # Verify the provided password against the stored hash
            if verify_password(password, stored_hashed_password):
                return (user_id, username)
        
        return None  # Invalid credentials
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None
    finally:
        conn.close()

def save_user_profile(user_id, profile_data):
    """Save or update user profile"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Check if profile exists
        c.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
        existing_profile = c.fetchone()
        
        if existing_profile:
            # Update existing profile
            c.execute('''
                UPDATE user_profiles SET 
                name=?, age=?, height=?, weight=?, gender=?, goal=?, 
                diet_preference=?, allergies=?, injuries=?, lifestyle=?, 
                updated_at=?
                WHERE user_id=?
            ''', (
                profile_data['Name'], profile_data['Age'], profile_data['Height'],
                profile_data['Weight'], profile_data['Gender'], profile_data['Goal'],
                profile_data['Diet Preference'], 
                json.dumps(profile_data['Allergies']),
                json.dumps(profile_data['Injuries']),
                profile_data['Lifestyle'],
                datetime.now(), user_id
            ))
        else:
            # Insert new profile
            c.execute('''
                INSERT INTO user_profiles 
                (user_id, name, age, height, weight, gender, goal, diet_preference, allergies, injuries, lifestyle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, profile_data['Name'], profile_data['Age'], profile_data['Height'],
                profile_data['Weight'], profile_data['Gender'], profile_data['Goal'],
                profile_data['Diet Preference'], 
                json.dumps(profile_data['Allergies']),
                json.dumps(profile_data['Injuries']),
                profile_data['Lifestyle']
            ))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving profile: {str(e)}")
        return False
    finally:
        conn.close()

def load_user_profile(user_id):
    """Load user profile data"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = c.fetchone()
        
        if profile:
            # Convert back to dictionary format using json
            return {
                'Name': profile[2],
                'Age': profile[3],
                'Height': profile[4],
                'Weight': profile[5],
                'Gender': profile[6],
                'Goal': profile[7],
                'Diet Preference': profile[8],
                'Allergies': json.loads(profile[9]) if profile[9] else [],
                'Injuries': json.loads(profile[10]) if profile[10] else [],
                'Lifestyle': profile[11]
            }
        return None
    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")
        return None
    finally:
        conn.close()

def get_all_users():
    """Get all users for admin panel"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT u.id, u.username, u.email, u.created_at, 
                   COUNT(up.id) as has_profile
            FROM users u 
            LEFT JOIN user_profiles up ON u.id = up.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        ''')
        users = c.fetchall()
        return users
    except Exception as e:
        return []
    finally:
        conn.close()

def get_user_stats():
    """Get user statistics"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM user_profiles")
        total_profiles = c.fetchone()[0]
        
        c.execute("SELECT username, created_at FROM users ORDER BY created_at DESC LIMIT 1")
        latest_user = c.fetchone()
        
        return {
            'total_users': total_users,
            'total_profiles': total_profiles,
            'latest_user': latest_user[0] if latest_user else 'None',
            'latest_signup': latest_user[1] if latest_user else 'None'
        }
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

# Initialize database when module is imported
init_db()