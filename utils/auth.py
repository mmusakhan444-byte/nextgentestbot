import streamlit as st
import hashlib
import sqlite3
from datetime import datetime
import os

def init_auth():
    """Initialize authentication database"""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            plan TEXT DEFAULT 'basic',
            created_at TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password, plan='basic'):
    """Create new user account"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, email, password, plan, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, hash_password(password), plan, datetime.now()))
        
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists!"
    except Exception as e:
        return False, str(e)

def check_login(username, password):
    """Verify login credentials - FIXED: Returns email too"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, email, plan FROM users 
            WHERE (username = ? OR email = ?) AND password = ?
        ''', (username, username, hash_password(password)))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Update last login
            conn = sqlite3.connect('data/users.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE username = ?
            ''', (datetime.now(), result[0]))
            conn.commit()
            conn.close()
            
            return True, result[0], result[2], result[1]  # username, plan, email
        return False, None, None, None
    except Exception as e:
        return False, None, None, None

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.plan = "basic"
    st.session_state.page = "Login"

def update_user_plan(username, new_plan):
    """Update user's plan"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET plan = ? WHERE username = ?
        ''', (new_plan, username))
        
        conn.commit()
        conn.close()
        st.session_state.plan = new_plan
        return True
    except Exception as e:
        return False