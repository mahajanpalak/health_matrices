# database.py
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import hashlib

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    """Verify a stored password against one provided by user"""
    return hash_password(plain_password) == hashed_password

def init_db():
    """Initialize the database and create tables"""
    conn = sqlite3.connect('health_app.db')
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
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, password, email=""):
    """Create a new user with hashed password"""
    conn = sqlite3.connect('health_app.db')
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
    conn = sqlite3.connect('health_app.db')
    c = conn.cursor()
    
    # Get the stored hashed password
    c.execute(
        "SELECT id, username, password FROM users WHERE username = ?",
        (username,)
    )
    user = c.fetchone()
    conn.close()
    
    if user:
        user_id, username, stored_hashed_password = user
        # Verify the provided password against the stored hash
        if verify_password(password, stored_hashed_password):
            return (user_id, username)
    
    return None  # Invalid credentials

def save_user_profile(user_id, profile_data):
    """Save or update user profile"""
    conn = sqlite3.connect('health_app.db')
    c = conn.cursor()
    
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
            profile_data['Diet Preference'], str(profile_data['Allergies']),
            str(profile_data['Injuries']), profile_data['Lifestyle'],
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
            profile_data['Diet Preference'], str(profile_data['Allergies']),
            str(profile_data['Injuries']), profile_data['Lifestyle']
        ))
    
    conn.commit()
    conn.close()

def load_user_profile(user_id):
    """Load user profile data"""
    conn = sqlite3.connect('health_app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    conn.close()
    
    if profile:
        # Convert back to dictionary format
        return {
            'Name': profile[2],
            'Age': profile[3],
            'Height': profile[4],
            'Weight': profile[5],
            'Gender': profile[6],
            'Goal': profile[7],
            'Diet Preference': profile[8],
            'Allergies': eval(profile[9]) if profile[9] else [],
            'Injuries': eval(profile[10]) if profile[10] else [],
            'Lifestyle': profile[11]
        }
    return None

# Initialize database when module is imported
init_db()