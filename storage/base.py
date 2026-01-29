"""Base storage interface for object storage."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def put(self, key: str, data: bytes) -> str:
        """
        Store data with the given key.

        Args:
            key: Object key/path
            data: Binary data to store

        Returns:
            URL or path to the stored object
        """
        pass

    @abstractmethod
    def get(self, key: str) -> bytes:
        """
        Retrieve data by key.

        Args:
            key: Object key/path

        Returns:
            Binary data
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete object by key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if object exists."""
        pass

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Get public/accessible URL for the object."""
        pass
