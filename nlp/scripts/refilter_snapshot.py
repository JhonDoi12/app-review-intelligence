"""Hitung ulang lang dan exclude_reason pada snapshot dengan filter terbaru.

Tanpa scraping ulang. Snapshot asli tidak diubah; hasilnya ditulis sebagai
berkas baru berakhiran _v2 beserta ringkasan JSON.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from review_nlp.ingestion import lang_filter
from review_nlp.ingestion.transform import refilter


def status(df: pd.DataFrame) -> pd.Series:
    return df["exclude_reason"].fillna("dipakai")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", help="path snapshot .parquet (v1)")
    p.add_argument("--suffix", default="_v2")
    args = p.parse_args()

    src = Path(args.file)
    before = pd.read_parquet(src)
    after = refilter(before)

    print("Status sebelum:")
    print(status(before).value_counts().to_string())
    print("\nStatus sesudah:")
    print(status(after).value_counts().to_string())
    print("\nPerpindahan status:")
    print(
        pd.crosstab(
            status(before), status(after), rownames=["sebelum"], colnames=["sesudah"]
        ).to_string()
    )

    out = src.with_name(f"{src.stem}{args.suffix}.parquet")
    after.to_parquet(out, index=False)

    meta = {
        "sumber": src.name,
        "dibuat": datetime.now(UTC).isoformat(timespec="seconds"),
        "baris": len(after),
        "filter": {
            "min_words": lang_filter.MIN_WORDS,
            "min_prob": lang_filter.MIN_PROB,
            "bahasa_asing": sorted(lang_filter.NON_ID_CLEAR),
            "jumlah_penanda_indonesia": len(lang_filter.ID_MARKERS),
        },
        "status_sebelum": {k: int(v) for k, v in status(before).value_counts().items()},
        "status_sesudah": {k: int(v) for k, v in status(after).value_counts().items()},
    }
    meta_path = out.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDitulis: {out}\nRingkasan: {meta_path}")


if __name__ == "__main__":
    main()
