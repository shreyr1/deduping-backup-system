import os
import shutil

class RestoreManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def restore_snapshot(self, snapshot_id, restore_path):
        """Restores all files from a specific snapshot to the target path."""
        entries = self.db.get_snapshot_entries(snapshot_id)
        if not entries:
            print(f"No entries found for snapshot {snapshot_id}")
            return False

        os.makedirs(restore_path, exist_ok=True)
        print(f"Restoring snapshot {snapshot_id} to {restore_path}...")
        
        restored_count = 0
        for rel_path, storage_path, _ in entries:
            target_file_path = os.path.join(restore_path, rel_path)
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            
            try:
                shutil.copy2(storage_path, target_file_path)
                restored_count += 1
            except (OSError, IOError) as e:
                print(f"Error restoring {rel_path}: {e}")
                
        print(f"Restore complete. {restored_count} files restored.")
        return True
