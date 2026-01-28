"""Local file system storage backend."""

import os
from pathlib import Path
from typing import Optional
from .base import StorageBackend


class LocalStorage(StorageBackend):
    """File system based storage backend."""

    def __init__(self, base_path: str = "storage"):
        """
        Initialize local storage.

        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, key: str) -> Path:
        """Get full file path for a key."""
        # Prevent directory traversal
        sanitized_key = key.lstrip("/").replace("..", "")
        full_path = self.base_path / sanitized_key

        # Ensure path is within base_path
        if not full_path.resolve().is_relative_to(self.base_path.resolve()):
            raise ValueError(f"Invalid key: {key}")

        return full_path

    def put(self, key: str, data: bytes) -> str:
        """Store data locally."""
        full_path = self._get_full_path(key)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(data)

        return str(full_path)

    def get(self, key: str) -> bytes:
        """Retrieve data from local storage."""
        full_path = self._get_full_path(key)

        if not full_path.exists():
            raise FileNotFoundError(f"Object not found: {key}")

        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, key: str) -> None:
        """Delete local file."""
        full_path = self._get_full_path(key)

        if full_path.exists():
            full_path.unlink()

    def exists(self, key: str) -> bool:
        """Check if file exists."""
        full_path = self._get_full_path(key)
        return full_path.exists()

    def get_url(self, key: str) -> str:
        """Get file path as URL."""
        return f"file://{self._get_full_path(key).absolute()}"
