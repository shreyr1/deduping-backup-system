import os
import shutil
from backup.utils import calculate_file_hash

class Deduper:
    def __init__(self, db_manager, storage_dir="storage"):
        self.db = db_manager
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def process_file(self, file_path, size):
        """Processes a file: hashes it and stores it if it's unique."""
        file_hash = calculate_file_hash(file_path)
        if not file_hash:
            return None

        if self.db.file_exists(file_hash):
            # Already exists in storage, just increment ref count in DB via add_file
            self.db.add_file(file_hash, None, size) 
            return file_hash

        # New file content, copy to storage
        # Use first 2 chars of hash as a subfolder to avoid thousands of files in one dir
        hash_prefix = file_hash[:2]
        dest_dir = os.path.join(self.storage_dir, hash_prefix)
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_path = os.path.join(dest_dir, file_hash)
        
        try:
            shutil.copy2(file_path, dest_path)
            self.db.add_file(file_hash, dest_path, size)
            return file_hash
        except (OSError, IOError) as e:
            print(f"Error copying file {file_path}: {e}")
            return None
