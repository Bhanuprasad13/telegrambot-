import sqlite3
from datetime import datetime
import logging

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.setup_database()
    
    def setup_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    task_type TEXT,
                    description TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    scheduled_for TIMESTAMP
                )
            ''')
            
            # Media table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media (
                    id INTEGER PRIMARY KEY,
                    type TEXT,
                    content TEXT,
                    caption TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP
                )
            ''')
            
            # Group messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_messages (
                    id INTEGER PRIMARY KEY,
                    group_id INTEGER,
                    user_id INTEGER,
                    message TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            # Polls table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS polls (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    question TEXT,
                    options TEXT,
                    message_id INTEGER,
                    created_at TIMESTAMP
                )
            ''')
            
            # Poll answers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS poll_answers (
                    id INTEGER PRIMARY KEY,
                    poll_id TEXT,
                    user_id INTEGER,
                    option_ids TEXT,
                    answered_at TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_task(self, user_id, task_type, description, scheduled_time):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (user_id, task_type, description, status, created_at, scheduled_for)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, task_type, description, 'pending', datetime.now(), 
                 datetime.now().timestamp() + scheduled_time))
            return cursor.lastrowid
    
    def list_tasks(self, user_id, status=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND status = ?', 
                             (user_id, status))
            else:
                cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
            return cursor.fetchall()
    
    def save_media(self, media_type, content, caption, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO media (type, content, caption, user_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (media_type, content, caption, user_id, datetime.now()))
            
    def save_group_message(self, group_id, user_id, message):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO group_messages (group_id, user_id, message, created_at)
                VALUES (?, ?, ?, ?)
            ''', (group_id, user_id, message, datetime.now()))
    
    def save_poll(self, user_id, poll_data):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO polls (user_id, question, options, message_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, poll_data['question'], poll_data['options'], 
                 poll_data['message_id'], datetime.now()))
    
    def save_poll_answer(self, poll_id, user_id, option_ids):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO poll_answers (poll_id, user_id, option_ids, answered_at)
                VALUES (?, ?, ?, ?)
            ''', (poll_id, user_id, ','.join(map(str, option_ids)), datetime.now()))
    
    def close(self):
        pass