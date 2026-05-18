import os

class Scanner:
    def __init__(self, root_path, ignore_list=None):
        self.root_path = os.path.abspath(root_path)
        self.ignore_list = ignore_list or ['.git', '__pycache__', '.DS_Store', 'node_modules']

    def scan(self):
        """Recursively scans the directory and yields file metadata."""
        for root, dirs, files in os.walk(self.root_path):
            # Filter directories in-place to skip ignored ones
            dirs[:] = [d for d in dirs if d not in self.ignore_list]
            
            for file_name in files:
                if file_name in self.ignore_list:
                    continue
                
                full_path = os.path.join(root, file_name)
                try:
                    stats = os.stat(full_path)
                    yield {
                        'full_path': full_path,
                        'relative_path': os.path.relpath(full_path, self.root_path),
                        'size': stats.st_size,
                        'mtime': stats.st_mtime
                    }
                except (OSError, IOError) as e:
                    print(f"Skipping {full_path}: {e}")
