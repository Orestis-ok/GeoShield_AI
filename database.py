"""
Local SQLite Database
"""
import sqlite3
import os


class Database:
    def __init__(self):
        self.db_path = 'data/geoshield.db'
        self._ensure_data_dir()
        self._init_db()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs('data', exist_ok=True)
    
    def _init_db(self):
        """Initialize database with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disasters (
                id INTEGER PRIMARY KEY,
                city TEXT,
                event_type TEXT,
                severity TEXT,
                year INTEGER
            )
        ''')
        
        # Check if we need to add sample data
        cursor.execute('SELECT COUNT(*) FROM disasters')
        if cursor.fetchone()[0] == 0:
            # Add sample data
            samples = [
                ('Athens', 'flood', 'high', 2020),
                ('Athens', 'fire', 'critical', 2018),
                ('Los Angeles', 'fire', 'critical', 2018),
                ('New Orleans', 'flood', 'critical', 2005),
                ('Tokyo', 'landslide', 'high', 2018),
            ]
            cursor.executemany(
                'INSERT INTO disasters (city, event_type, severity, year) VALUES (?, ?, ?, ?)',
                samples
            )
            conn.commit()
        
        conn.close()
    
    def count_events_near(self, city):
        """Count historical events near city"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT COUNT(*) FROM disasters WHERE LOWER(city) LIKE LOWER(?)',
            (f'%{city}%',)
        )
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
