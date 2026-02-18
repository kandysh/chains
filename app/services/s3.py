"""S3 helpers: presigned URL generation and key validation."""

import logging
import uuid
from pathlib import PurePosixPath

import boto3
from botocore.exceptions import ClientError

from app.config import Settings
from app.schemas.upload import PresignedUrlItem

logger = logging.getLogger(__name__)


def _s3_client(settings: Settings):
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


async def generate_presigned_post_urls(
    filenames: list[str],
    user_id: str,
    settings: Settings,
) -> list[PresignedUrlItem]:
    """Generate presigned POST URLs for direct browser-to-S3 uploads.

    Each file is keyed under ``uploads/{user_id}/{uuid}/{filename}`` to ensure
    per-user isolation and collision-free storage.
    """
    client = _s3_client(settings)
    items: list[PresignedUrlItem] = []

    for filename in filenames:
        safe_name = PurePosixPath(filename).name  # strip any path traversal
        key = f"{settings.s3_upload_prefix}/{user_id}/{uuid.uuid4()}/{safe_name}"
        try:
            resp = client.generate_presigned_post(
                Bucket=settings.s3_bucket,
                Key=key,
                ExpiresIn=settings.presigned_url_expiry,
            )
            items.append(
                PresignedUrlItem(
                    filename=filename,
                    s3_key=key,
                    upload_url=resp["url"],
                    fields=resp["fields"],
                )
            )
        except ClientError as exc:
            logger.error("Failed to generate presigned URL for %s: %s", filename, exc)
            raise

    return items


async def validate_s3_key(key: str, settings: Settings) -> None:
    """Assert that a given S3 key exists in the configured bucket.

    Raises ``ValueError`` if the key is outside the expected prefix or the
    object does not exist.
    """
    if not key.startswith(settings.s3_upload_prefix + "/"):
        raise ValueError(f"S3 key '{key}' is outside the allowed prefix")

    client = _s3_client(settings)
    try:
        client.head_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey"):
            raise ValueError(f"S3 object not found: {key}") from exc
        raise
