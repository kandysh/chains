"""Pydantic schemas for the /upload-urls endpoint."""

from pydantic import BaseModel


class PresignedUrlRequest(BaseModel):
    filenames: list[str]  # e.g. ["bookings.xlsx", "confirmations.pdf"]


class PresignedUrlItem(BaseModel):
    filename: str
    s3_key: str
    upload_url: str      # presigned POST URL for the browser
    fields: dict         # S3 presigned POST fields (policy, signature, etc.)


class PresignedUrlResponse(BaseModel):
    urls: list[PresignedUrlItem]
