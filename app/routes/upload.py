"""GET /upload-urls — generate presigned S3 upload URLs for the browser."""

import logging

from fastapi import APIRouter

from app.dependencies import AppSettings, CurrentUser
from app.schemas.upload import PresignedUrlRequest, PresignedUrlResponse
from app.services.s3 import generate_presigned_post_urls

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload-urls", tags=["upload"])


@router.get("", response_model=PresignedUrlResponse)
async def get_upload_urls(
    filenames: str,  # comma-separated; kept simple for GET qs
    current_user: CurrentUser,
    settings: AppSettings,
) -> PresignedUrlResponse:
    """Return presigned S3 POST URLs so the browser can upload directly.

    Each URL expires in 15 minutes (``presigned_url_expiry``).
    The browser should upload files directly to S3 using these URLs and then
    submit the returned ``s3_key`` values to ``POST /process``.
    """
    name_list = [n.strip() for n in filenames.split(",") if n.strip()]
    user_id: str = current_user["sub"]
    items = await generate_presigned_post_urls(name_list, user_id, settings)
    return PresignedUrlResponse(urls=items)
