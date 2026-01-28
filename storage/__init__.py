"""Storage module for object storage abstraction."""

from .base import StorageBackend
from .local import LocalStorage
from .s3 import S3Storage
from .factory import get_storage

__all__ = ["StorageBackend", "LocalStorage", "S3Storage", "get_storage"]
