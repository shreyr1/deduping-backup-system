import argparse
import sys
import os
from backup.database import DatabaseManager
from backup.snapshot import SnapshotManager
from backup.restore import RestoreManager
from backup.utils import format_size

def main():
    parser = argparse.ArgumentParser(description="Deduping Backup System - A simple deduplicated backup tool.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a new backup snapshot")
    backup_parser.add_argument("path", help="Directory path to backup")
    backup_parser.add_argument("-m", "--message", default="No description", help="Snapshot description")

    # List command
    subparsers.add_parser("list", help="List all backup snapshots")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore a snapshot")
    restore_parser.add_argument("snapshot_id", type=int, help="ID of the snapshot to restore")
    restore_parser.add_argument("dest", help="Destination directory for restoration")

    # Stats command
    subparsers.add_parser("stats", help="Show storage savings and statistics")

    args = parser.parse_args()

    # Initialize components
    db_manager = DatabaseManager()
    snapshot_manager = SnapshotManager(db_manager)
    restore_manager = RestoreManager(db_manager)

    if args.command == "backup":
        if not os.path.isdir(args.path):
            print(f"Error: {args.path} is not a valid directory.")
            sys.exit(1)
        snapshot_id = snapshot_manager.create_snapshot(args.path, args.message)
        print(f"Successfully created snapshot {snapshot_id}")

    elif args.command == "list":
        snapshots = snapshot_manager.list_snapshots()
        if not snapshots:
            print("No snapshots found.")
        else:
            print(f"{'ID':<5} | {'Timestamp':<20} | {'Description':<20} | {'Root Path'}")
            print("-" * 70)
            for snip in snapshots:
                print(f"{snip[0]:<5} | {snip[1]:<20} | {snip[2]:<20} | {snip[3]}")

    elif args.command == "restore":
        success = restore_manager.restore_snapshot(args.snapshot_id, args.dest)
        if not success:
            sys.exit(1)

    elif args.command == "stats":
        stats = db_manager.get_stats()
        print("Storage Statistics:")
        print(f"  Total Logical Size:  {format_size(stats['total_size'])}")
        print(f"  Actual Physical Size: {format_size(stats['unique_size'])}")
        print(f"  Total Savings:       {format_size(stats['savings'])}")
        if stats['total_size'] > 0:
            ratio = (stats['savings'] / stats['total_size']) * 100
            print(f"  Deduplication Ratio: {ratio:.2f}%")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
