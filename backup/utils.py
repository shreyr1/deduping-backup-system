import hashlib

def calculate_file_hash(file_path, chunk_size=8192):
    """Calculates SHA-256 hash of a file in chunks to handle large files efficiently."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (OSError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return None

def format_size(size_bytes):
    """Formats bytes into a human-readable string."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"
