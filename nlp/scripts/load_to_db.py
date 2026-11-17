"""Muat snapshot Parquet ke PostgreSQL. Aman dijalankan berulang."""

import argparse
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

INSERT_APP = text(
    "INSERT INTO apps (package_name, name) VALUES (:pkg, :name) "
    "ON CONFLICT (package_name) DO UPDATE SET name = EXCLUDED.name RETURNING id"
)
INSERT_VERSION = text(
    "INSERT INTO app_versions (app_id, version_name) VALUES (:app_id, :v) "
    "ON CONFLICT (app_id, version_name) DO NOTHING"
)
INSERT_REVIEW = text(
    "INSERT INTO reviews (app_id, external_id, user_hash, rating, text_raw, thumbs_up, "
    "app_version, reviewed_at, lang, exclude_reason) VALUES (:app_id, :external_id, "
    ":user_hash, :rating, :text_raw, :thumbs_up, :app_version, :reviewed_at, :lang, "
    ":exclude_reason) ON CONFLICT (external_id) DO NOTHING"
)
COUNT_REVIEWS = text("SELECT count(*) FROM reviews WHERE app_id = :a")
COLUMNS = [
    "external_id",
    "user_hash",
    "rating",
    "text_raw",
    "thumbs_up",
    "app_version",
    "reviewed_at",
    "lang",
    "exclude_reason",
]


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", help="path file .parquet hasil scrape.py")
    p.add_argument("--app", default=os.getenv("TARGET_APP_PACKAGE", "com.whatsapp"))
    p.add_argument("--app-name", default="WhatsApp")
    args = p.parse_args()

    url = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
    if not url:
        p.error("Set DATABASE_URL_LOCAL di .env")
    if "@db:" in url:
        p.error("Dari Ubuntu pakai DATABASE_URL_LOCAL (host localhost), bukan host 'db'")

    df = pd.read_parquet(args.file)
    df["reviewed_at"] = pd.to_datetime(df["reviewed_at"])
    if df["reviewed_at"].dt.tz is None:
        df["reviewed_at"] = df["reviewed_at"].dt.tz_localize("UTC")
    df = df[COLUMNS].astype(object).where(df[COLUMNS].notna(), None)

    records = df.to_dict("records")
    for r in records:
        r["reviewed_at"] = r["reviewed_at"].to_pydatetime()
    versions = sorted({r["app_version"] for r in records if r["app_version"]})

    engine = create_engine(url)
    with engine.begin() as conn:
        app_id = conn.execute(INSERT_APP, {"pkg": args.app, "name": args.app_name}).scalar_one()
        before = conn.execute(COUNT_REVIEWS, {"a": app_id}).scalar_one()
        if versions:
            conn.execute(INSERT_VERSION, [{"app_id": app_id, "v": v} for v in versions])
        for i in range(0, len(records), 1000):
            chunk = [{**r, "app_id": app_id} for r in records[i : i + 1000]]
            conn.execute(INSERT_REVIEW, chunk)
        after = conn.execute(COUNT_REVIEWS, {"a": app_id}).scalar_one()

    print(f"Di file: {len(records)} | baru masuk: {after - before} | total di DB: {after}")


if __name__ == "__main__":
    main()
