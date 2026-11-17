"""Scrape ulasan Play Store dalam satu jendela waktu dan simpan sebagai snapshot."""

import argparse
import logging
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from review_nlp.ingestion.scraper import scrape_window
from review_nlp.ingestion.transform import to_frame


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--app", default=os.getenv("TARGET_APP_PACKAGE", "com.whatsapp"))
    p.add_argument("--since", default=os.getenv("SCRAPE_SINCE"))
    p.add_argument("--until", default=os.getenv("SCRAPE_UNTIL"))
    p.add_argument("--lang", default=os.getenv("SCRAPE_LANG", "id"))
    p.add_argument("--country", default=os.getenv("SCRAPE_COUNTRY", "id"))
    p.add_argument(
        "--max-per-week",
        type=int,
        default=int(os.getenv("SCRAPE_MAX_PER_WEEK", "800")),
    )
    p.add_argument("--sleep", type=float, default=float(os.getenv("SCRAPE_SLEEP_SECONDS", "1.5")))
    p.add_argument("--out-dir", default="data/raw")
    args = p.parse_args()

    if not args.since or not args.until:
        p.error("Isi --since dan --until (atau SCRAPE_SINCE/SCRAPE_UNTIL di .env)")
    since, until = date.fromisoformat(args.since), date.fromisoformat(args.until)
    if since > until:
        p.error("--since harus sebelum atau sama dengan --until")

    salt = os.getenv("USER_HASH_SALT", "")
    if salt in ("", "change_me"):
        p.error("Isi USER_HASH_SALT di .env dengan nilai acak (bukan 'change_me')")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    rows = scrape_window(
        args.app, since, until, args.lang, args.country, args.max_per_week, args.sleep
    )
    if not rows:
        raise SystemExit("Tidak ada ulasan pada jendela waktu ini.")

    df = to_frame(rows, salt, since)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{args.app}_{since}_{until}"
    df.to_parquet(out_dir / f"{stem}.parquet", index=False)
    df.to_csv(out_dir / f"{stem}.csv", index=False)

    print(f"\nSnapshot: {out_dir / (stem + '.parquet')}")
    print(f"Total ulasan: {len(df)}")
    print("\nAlasan eksklusi:")
    print(df["exclude_reason"].fillna("dipakai").value_counts().to_string())
    print("\nDistribusi rating:")
    print(df["rating"].value_counts().sort_index().to_string())
    print("\nUlasan per minggu:")
    print(df["week_index"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
