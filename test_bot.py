import unittest
import os
import sqlite3
import time
from contextlib import contextmanager

class DatabaseTestBase:
    """Base class for database testing with improved connection handling"""
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    @classmethod
    def remove_db_file(cls):
        """Safely remove database file with retries"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if os.path.exists(cls.db_path):
                    os.remove(cls.db_path)
                return
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise

class TestDatabaseManager(DatabaseTestBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = 'test_bot.db'
        cls.remove_db_file()

    def setUp(self):
        """Set up fresh database instance for each test"""
        from database import DatabaseManager
        self.db = DatabaseManager(self.db_path)
        self.test_user_id = 12345
        self.test_group_id = 67890
        self.clear_all_tasks()

    def tearDown(self):
        """Ensure proper cleanup after each test"""
        if hasattr(self, 'db'):
            self.db.close()
            delattr(self, 'db')  # Remove reference to allow garbage collection
        
        # Force garbage collection and give system time to release file handles
        import gc
        gc.collect()
        time.sleep(0.1)
        
        self.remove_db_file()

    def clear_all_tasks(self):
        """Clear all tasks with proper connection handling"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE user_id = ?', (self.test_user_id,))
            conn.commit()

    def test_add_task(self):
        """Test adding a task with proper connection handling"""
        task_id = self.db.add_task(
            self.test_user_id,
            'scheduled',
            'Test Task Description',
            3600
        )

        # Verify task was added using a separate connection
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (self.test_user_id,))
            tasks = cursor.fetchall()
            
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][1], self.test_user_id)
        self.assertEqual(tasks[0][3], 'Test Task Description')

    def test_list_tasks(self):
        """Test listing tasks with proper connection handling"""
        # Add multiple tasks
        self.db.add_task(self.test_user_id, 'scheduled', 'Task 1', 3600)
        self.db.add_task(self.test_user_id, 'scheduled', 'Task 2', 7200)

        # Test listing all tasks
        tasks = self.db.list_tasks(self.test_user_id)
        self.assertEqual(len(tasks), 2)

        # Test listing tasks by status
        tasks_pending = self.db.list_tasks(self.test_user_id, status='pending')
        self.assertEqual(len(tasks_pending), 2)

    def test_save_media_photo(self):
        """Test saving photo media with proper connection handling"""
        self.db.save_media(
            'photo',
            'test_photo.jpg',
            'Test photo caption',
            self.test_user_id
        )

        # Verify in database using a separate connection
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM media WHERE type = ? AND user_id = ?',
                ('photo', self.test_user_id)
            )
            result = cursor.fetchall()
            
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][3], 'Test photo caption')

class TestDatabaseManagerEdgeCases(DatabaseTestBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = 'test_bot.db'
        cls.remove_db_file()

    def setUp(self):
        from database import DatabaseManager
        self.db = DatabaseManager(self.db_path)
        self.test_user_id = 12345
        self.test_group_id = 67890
        self.clear_all_tasks()

    def tearDown(self):
        if hasattr(self, 'db'):
            self.db.close()
            delattr(self, 'db')
        
        import gc
        gc.collect()
        time.sleep(0.1)
        
        self.remove_db_file()

    def clear_all_tasks(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE user_id = ?', (self.test_user_id,))
            conn.commit()

    def test_edge_case_empty_database(self):
        """Test edge case where no tasks exist"""
        tasks = self.db.list_tasks(self.test_user_id)
        self.assertEqual(len(tasks), 0)

    def test_edge_case_duplicate_task(self):
        """Test adding a duplicate task"""
        self.db.add_task(self.test_user_id, 'scheduled', 'Task 1', 3600)
        self.db.add_task(self.test_user_id, 'scheduled', 'Task 1', 3600)

        tasks = self.db.list_tasks(self.test_user_id)
        self.assertEqual(len(tasks), 2)

if __name__ == '__main__':
    unittest.main()