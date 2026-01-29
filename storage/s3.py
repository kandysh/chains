"""S3-compatible storage backend."""

import boto3
from botocore.exceptions import ClientError
from typing import Optional
from .base import StorageBackend


class S3Storage(StorageBackend):
    """S3 and S3-compatible storage backend (MinIO, etc)."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key (uses env if not provided)
            aws_secret_access_key: AWS secret key (uses env if not provided)
            region_name: AWS region
            endpoint_url: Custom endpoint URL (for MinIO, etc)
        """
        self.bucket_name = bucket_name

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.s3_client.create_bucket(Bucket=self.bucket_name)

    def put(self, key: str, data: bytes) -> str:
        """Upload data to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
            )
            return self.get_url(key)
        except ClientError as e:
            raise Exception(f"Failed to upload object: {e}")

    def get(self, key: str) -> bytes:
        """Download data from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            raise FileNotFoundError(f"Object not found: {key}") from e

    def delete(self, key: str) -> None:
        """Delete object from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            raise Exception(f"Failed to delete object: {e}")

    def exists(self, key: str) -> bool:
        """Check if object exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def get_url(self, key: str) -> str:
        """Get S3 URL for the object."""
        return f"s3://{self.bucket_name}/{key}"
