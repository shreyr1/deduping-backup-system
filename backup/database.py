import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="backups/metadata.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for file content (deduplication)
            # hash: SHA-256 of the file content
            # storage_path: Path where the actual unique file is stored
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    hash TEXT PRIMARY KEY,
                    storage_path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    ref_count INTEGER DEFAULT 1
                )
            ''')

            # Table for backup snapshots
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    root_path TEXT NOT NULL
                )
            ''')

            # Table for file entries in a snapshot
            # Links snapshots to files
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshot_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    last_modified REAL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots (id),
                    FOREIGN KEY (file_hash) REFERENCES files (hash)
                )
            ''')
            
            conn.commit()

    def add_snapshot(self, description, root_path):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snapshots (description, root_path) VALUES (?, ?)",
                (description, root_path)
            )
            return cursor.lastrowid

    def file_exists(self, file_hash):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM files WHERE hash = ?", (file_hash,))
            return cursor.fetchone() is not None

    def add_file(self, file_hash, storage_path, size):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # If hash exists, increment ref_count, else insert
            cursor.execute("SELECT ref_count FROM files WHERE hash = ?", (file_hash,))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE files SET ref_count = ref_count + 1 WHERE hash = ?",
                    (file_hash,)
                )
            else:
                cursor.execute(
                    "INSERT INTO files (hash, storage_path, size) VALUES (?, ?, ?)",
                    (file_hash, storage_path, size)
                )
            conn.commit()

    def add_snapshot_entry(self, snapshot_id, file_path, file_hash, last_modified):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snapshot_entries (snapshot_id, file_path, file_hash, last_modified) VALUES (?, ?, ?, ?)",
                (snapshot_id, file_path, file_hash, last_modified)
            )
            conn.commit()

    def get_snapshots(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, description, root_path FROM snapshots ORDER BY timestamp DESC")
            return cursor.fetchall()

    def get_snapshot_entries(self, snapshot_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT se.file_path, f.storage_path, f.hash 
                FROM snapshot_entries se
                JOIN files f ON se.file_hash = f.hash
                WHERE se.snapshot_id = ?
            ''', (snapshot_id,))
            return cursor.fetchall()
            
    def get_stats(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(size) FROM files")
            unique_size = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT SUM(f.size) 
                FROM snapshot_entries se
                JOIN files f ON se.file_hash = f.hash
            ''')
            total_size = cursor.fetchone()[0] or 0
            
            return {
                "unique_size": unique_size,
                "total_size": total_size,
                "savings": total_size - unique_size
            }
