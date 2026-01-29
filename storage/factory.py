"""Storage backend factory."""

import os
from functools import lru_cache
from typing import Optional
from .base import StorageBackend
from .local import LocalStorage
from .s3 import S3Storage


@lru_cache()
def get_storage(storage_type: Optional[str] = None) -> StorageBackend:
    """
    Get storage backend instance.

    Args:
        storage_type: Type of storage ('local' or 's3'). If not provided, reads from env.

    Returns:
        Storage backend instance
    """
    if storage_type is None:
        storage_type = os.getenv("STORAGE_TYPE", "local")

    if storage_type == "s3":
        return S3Storage(
            bucket_name=os.getenv("S3_BUCKET_NAME", "confirmations"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        )
    else:
        return LocalStorage(
            base_path=os.getenv("STORAGE_PATH", "storage")
        )
