from datetime import date

import pandas as pd

from review_nlp.ingestion.anonymizer import hash_user, mask_pii
from review_nlp.ingestion.lang_filter import analyze_text
from review_nlp.ingestion.scraper import week_index

COLUMNS = [
    "external_id",
    "user_hash",
    "rating",
    "text_raw",
    "thumbs_up",
    "app_version",
    "reviewed_at",
    "week_index",
    "lang",
    "exclude_reason",
]


def to_frame(rows: list[dict], salt: str, since: date) -> pd.DataFrame:
    """Ubah hasil scraper menjadi tabel bersih: identitas di-hash, PII dimasking."""
    records = []
    for row in rows:
        text = mask_pii((row.get("content") or "").strip())
        lang, reason = analyze_text(text)
        reviewed_at = row["at"]
        records.append(
            {
                "external_id": row["reviewId"],
                "user_hash": hash_user(row.get("userName") or "", salt),
                "rating": int(row["score"]),
                "text_raw": text,
                "thumbs_up": int(row.get("thumbsUpCount") or 0),
                "app_version": row.get("reviewCreatedVersion") or row.get("appVersion"),
                "reviewed_at": reviewed_at,
                "week_index": week_index(reviewed_at.date(), since),
                "lang": lang,
                "exclude_reason": reason,
            }
        )
    return pd.DataFrame.from_records(records, columns=COLUMNS)
