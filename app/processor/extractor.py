"""Phase 2 — LLM Extraction.

Downloads the confirmation PDF from S3 and submits it to a multi-modal LLM
(GPT-4o) with a structured-output schema.  Returns a list of
``ExtractedAllocation`` objects with per-field confidence scores.

Accuracy strategy:
  1. Structured output mode — schema enforced by the model, no free-text parsing.
  2. Alias injection — known counterparty / instrument aliases prepended to the
     prompt so the model resolves ambiguous names at extraction time.
  3. Per-field confidence scores — fields below threshold are flagged for review.
"""

import base64
import json
import logging

import boto3
from openai import AsyncOpenAI

from app.config import Settings
from app.processor.schemas import ExtractionResult, ExtractedAllocation

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.80  # Fields below this are flagged for review
MAX_RETRIES = 3


async def extract_allocations(
    job_id: str,
    s3_key: str,
    settings: Settings,
    alias_hints: dict | None = None,
) -> list[ExtractedAllocation]:
    """Download PDF and run multi-modal LLM extraction.

    Returns a list of ``ExtractedAllocation`` objects.
    Retries up to ``MAX_RETRIES`` times on schema validation failure.
    """
    logger.info("[%s] Extractor: downloading %s", job_id, s3_key)
    pdf_bytes = _download_from_s3(s3_key, settings)
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    prompt = _build_prompt(alias_hints or {})
    schema = ExtractionResult.model_json_schema()

    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:application/pdf;base64,{pdf_b64}"
                                },
                            },
                        ],
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": "ExtractionResult", "schema": schema},
                },
            )
            raw = response.choices[0].message.content
            result = ExtractionResult.model_validate_json(raw)
            logger.info(
                "[%s] Extractor: extracted %d allocations (attempt %d)",
                job_id,
                len(result.allocations),
                attempt,
            )
            return result.allocations
        except Exception as exc:
            logger.warning("[%s] Extractor attempt %d failed: %s", job_id, attempt, exc)
            last_exc = exc

    raise RuntimeError(
        f"[{job_id}] Extraction failed after {MAX_RETRIES} attempts"
    ) from last_exc


def _download_from_s3(key: str, settings: Settings) -> bytes:
    client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read()


def _build_prompt(alias_hints: dict) -> str:
    alias_section = ""
    if alias_hints:
        alias_section = (
            "Known entity aliases (use these to resolve ambiguous names):\n"
            + json.dumps(alias_hints, indent=2)
            + "\n\n"
        )
    return (
        f"{alias_section}"
        "Extract all trade allocations from this confirmation document.\n"
        "For each allocation return: counterparty, ISIN, CUSIP (if present), "
        "trade_date (YYYY-MM-DD), settlement_date (YYYY-MM-DD), quantity (numeric), "
        "price (numeric), side (BUY or SELL), currency (ISO 4217).\n"
        "For every field include a confidence score between 0 and 1.\n"
        "Return ONLY valid JSON matching the provided schema — no additional text."
    )
