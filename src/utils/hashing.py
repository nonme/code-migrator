"""File hashing utilities for verification."""

import hashlib
import logging
from pathlib import Path


class FileHasher:
    """Handles file hashing for verification purposes."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_file_hash(self, file_path: Path, algorithm: str = "md5") -> str:
        """
        Calculate hash of a file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')

        Returns:
            Hash as hex string
        """
        hash_func = getattr(hashlib, algorithm)()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
        except (OSError, PermissionError) as e:
            self.logger.error(f"Cannot read file {file_path}: {e}")
            return ""

        return hash_func.hexdigest()

    def verify_copy(self, source: Path, destination: Path) -> bool:
        """
        Verify that a file was copied correctly by comparing hashes.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if hashes match, False otherwise
        """
        if not destination.exists():
            return False

        source_hash = self.get_file_hash(source)
        dest_hash = self.get_file_hash(destination)

        return source_hash == dest_hash and source_hash != ""
