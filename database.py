import sqlite3

class DatabaseManager:
    def __init__(self, db_name="system_vault.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE, password TEXT, role TEXT, 
                access_level TEXT DEFAULT 'READ')""")
            
            self.conn.execute("""CREATE TABLE IF NOT EXISTS watched_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE, folder_path TEXT, last_hash TEXT,
                status TEXT DEFAULT 'SECURE')""")
                
            self.conn.execute("""CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event TEXT, user_id INTEGER)""")

            self.conn.execute("""CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, username TEXT, requested_level TEXT,
                folder_path TEXT, status TEXT DEFAULT 'PENDING')""")

    def query(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor