"""Phase 1 — Booking Indexer.

Downloads the booking Excel from S3, parses it into normalised rows, and loads
them into Redis for fast lookup during matching.

Redis key structure (all keys expire after 1 h):
    booking:{job_id}:idx:{isin}:{trade_date}  → Hash  (primary exact-match index)
    booking:{job_id}:cpty:{norm_counterparty} → Set   (secondary fuzzy-match index)
"""

import json
import logging
from io import BytesIO

import boto3
import pandas as pd

from app.config import Settings
from app.services.redis_client import get_redis

logger = logging.getLogger(__name__)

BOOKING_INDEX_TTL = 3600  # 1 hour

# Expected column names in the booking Excel (case-insensitive match applied)
REQUIRED_COLUMNS = {
    "booking_id",
    "isin",
    "trade_date",
    "settlement_date",
    "quantity",
    "price",
    "side",
    "currency",
    "counterparty",
}


async def index_bookings(job_id: str, s3_key: str, settings: Settings) -> int:
    """Download ``s3_key`` from S3, parse, and load into Redis.

    Returns the number of booking rows indexed.
    Raises ``ValueError`` if required columns are missing.
    """
    logger.info("[%s] Indexer: downloading %s", job_id, s3_key)
    xlsx_bytes = _download_from_s3(s3_key, settings)
    df = _parse_xlsx(xlsx_bytes)
    _validate_columns(df)
    df = _normalise(df)
    count = await _load_into_redis(job_id, df)
    logger.info("[%s] Indexer: indexed %d bookings", job_id, count)
    return count


def _download_from_s3(key: str, settings: Settings) -> bytes:
    client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read()


def _parse_xlsx(data: bytes) -> pd.DataFrame:
    return pd.read_excel(BytesIO(data), dtype=str)


def _validate_columns(df: pd.DataFrame) -> None:
    normalised = {c.lower().strip().replace(" ", "_") for c in df.columns}
    missing = REQUIRED_COLUMNS - normalised
    if missing:
        raise ValueError(f"Booking Excel missing required columns: {missing}")


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["counterparty_norm"] = (
        df["counterparty"].str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    )
    return df


async def _load_into_redis(job_id: str, df: pd.DataFrame) -> int:
    redis = await get_redis()
    pipe = redis.pipeline()

    for _, row in df.iterrows():
        data = row.to_dict()
        isin = str(data.get("isin", "")).upper()
        trade_date = str(data.get("trade_date", ""))
        counterparty_norm = str(data.get("counterparty_norm", ""))
        booking_id = str(data.get("booking_id", ""))

        primary_key = f"booking:{job_id}:idx:{isin}:{trade_date}"
        pipe.hset(primary_key, mapping={"data": json.dumps(data)})
        pipe.expire(primary_key, BOOKING_INDEX_TTL)

        cpty_key = f"booking:{job_id}:cpty:{counterparty_norm}"
        pipe.sadd(cpty_key, booking_id)
        pipe.expire(cpty_key, BOOKING_INDEX_TTL)

    await pipe.execute()
    return len(df)
