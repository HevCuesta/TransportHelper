import sqlite3
import os
from typing import List, Dict, Any, Optional
import threading

class DatabaseService:
    """A SQLite database service for managing user data in a Flet application."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.db_path = "transport_helper.db"
        self.conn = None
        self.initialize_database()
        self._initialized = True
    
    def initialize_database(self):
        """Create database and tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create user_preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    theme TEXT DEFAULT 'light',
                    favorite_routes TEXT,
                    last_login TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create saved_locations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    is_favorite BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    # User operations
    def create_user(self, username: str, password_hash: str, email: Optional[str] = None) -> int:
        """Create a new user and return the user ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            self.conn.commit()
            
            # Create default user preferences
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO user_preferences (user_id) VALUES (?)",
                (user_id,)
            )
            self.conn.commit()
            
            return user_id
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return -1
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                return None
                
            return {
                "id": user[0],
                "username": user[1],
                "password_hash": user[2],
                "email": user[3],
                "created_at": user[4]
            }
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_preferences(self, user_id: int, theme: Optional[str] = None, 
                               favorite_routes: Optional[str] = None) -> bool:
        """Update user preferences."""
        try:
            cursor = self.conn.cursor()
            updates = []
            values = []
            
            if theme is not None:
                updates.append("theme = ?")
                values.append(theme)
            
            if favorite_routes is not None:
                updates.append("favorite_routes = ?")
                values.append(favorite_routes)
            
            if not updates:
                return False
            
            values.append(user_id)
            query = f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = ?"
            
            cursor.execute(query, values)
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating preferences: {e}")
            return False
    
    # Location operations
    def add_location(self, user_id: int, name: str, address: str, 
                     latitude: float = None, longitude: float = None, 
                     is_favorite: bool = False) -> int:
        """Add a saved location for a user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO saved_locations 
                   (user_id, name, address, latitude, longitude, is_favorite) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, name, address, latitude, longitude, is_favorite)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding location: {e}")
            return -1
    
    def get_user_locations(self, user_id: int, favorites_only: bool = False) -> List[Dict[str, Any]]:
        """Get all saved locations for a user."""
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM saved_locations WHERE user_id = ?"
            params = [user_id]
            
            if favorites_only:
                query += " AND is_favorite = 1"
                
            cursor.execute(query, params)
            locations = cursor.fetchall()
            
            result = []
            for loc in locations:
                result.append({
                    "id": loc[0],
                    "user_id": loc[1],
                    "name": loc[2],
                    "address": loc[3],
                    "latitude": loc[4],
                    "longitude": loc[5],
                    "is_favorite": bool(loc[6])
                })
            
            return result
        except sqlite3.Error as e:
            print(f"Error getting locations: {e}")
            return []
    
    def update_login_timestamp(self, user_id: int) -> bool:
        """Update the last login timestamp for a user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE user_preferences SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", 
                (user_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating login timestamp: {e}")
            return False