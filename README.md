# Deduping Backup System

A lightweight, efficient command-line backup tool written in Python that uses content-based deduplication to save storage space.

## Features
- **Smart Deduplication**: Uses SHA-256 hashing to identify duplicate files. Identical files are stored only once.
- **Incremental Backups**: Only new or changed files are added to the storage, while existing files are referenced.
- **Snapshot Management**: Create, list, and restore from specific backup snapshots.
- **Storage Statistics**: View logical vs. physical storage size and see exactly how much space you've saved.
- **SQLite Backend**: Efficiently manages metadata, file hashes, and snapshot references.

## Tech Stack
- **Language**: Python 3
- **Database**: SQLite3
- **Storage**: Local File System

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd deduping-backup-system
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. No external dependencies are required for the core functionality as it uses Python's standard library.

## Usage

### Create a Backup
```bash
python3 main.py backup /path/to/source -m "Description of backup"
```

### List Snapshots
```bash
python3 main.py list
```

### View Statistics
```bash
python3 main.py stats
```

### Restore a Backup
```bash
python3 main.py restore <snapshot_id> /path/to/destination
```

## How it Works (Deduplication Logic)
1. **Scanning**: The system recursively scans the source directory.
2. **Hashing**: For every file, a SHA-256 hash of its content is calculated.
3. **Check**: The system checks the SQLite database if a file with the same hash already exists in the `storage/` directory.
4. **Store/Reference**: 
   - If unique: The file is copied to `storage/` and indexed.
   - If duplicate: Only a reference is created in the database for the new snapshot.
5. **Restore**: When restoring, the system looks up the hashes for the specific snapshot and copies the corresponding files from the central `storage/` to the destination.

## Project Structure
- `backup/`: Core modules (Scanner, Deduper, Database, etc.)
- `storage/`: Centralized store for unique file contents.
- `backups/`: Contains the SQLite metadata database.
- `main.py`: CLI entry point.

## License
MIT
