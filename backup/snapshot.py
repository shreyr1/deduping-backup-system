from backup.scanner import Scanner
from backup.deduper import Deduper

class SnapshotManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.deduper = Deduper(self.db)

    def create_snapshot(self, root_path, description):
        scanner = Scanner(root_path)
        snapshot_id = self.db.add_snapshot(description, root_path)
        
        print(f"Starting backup for: {root_path}")
        files_processed = 0
        
        for file_info in scanner.scan():
            file_hash = self.deduper.process_file(file_info['full_path'], file_info['size'])
            if file_hash:
                self.db.add_snapshot_entry(
                    snapshot_id, 
                    file_info['relative_path'], 
                    file_hash, 
                    file_info['mtime']
                )
                files_processed += 1
        
        print(f"Snapshot {snapshot_id} created. Processed {files_processed} files.")
        return snapshot_id

    def list_snapshots(self):
        return self.db.get_snapshots()
