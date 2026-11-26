"""Muat snapshot Parquet ke PostgreSQL. Aman dijalankan berulang.

Mode biasa: menambah ulasan baru, ulasan yang sudah ada dibiarkan.
Mode --refresh-filter: memperbarui kolom lang dan exclude_reason ulasan yang sudah ada.
"""

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
UPDATE_FILTER = text(
    "UPDATE reviews SET lang = :lang, exclude_reason = :exclude_reason "
    "WHERE app_id = :app_id AND external_id = :external_id"
)
STATUS_COUNTS = text(
    "SELECT coalesce(exclude_reason, 'dipakai') AS status, count(*) AS n "
    "FROM reviews WHERE app_id = :a GROUP BY 1 ORDER BY 2 DESC"
)
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
CHUNK = 1000


def read_records(path: str) -> list[dict]:
    df = pd.read_parquet(path)
    df["reviewed_at"] = pd.to_datetime(df["reviewed_at"])
    if df["reviewed_at"].dt.tz is None:
        df["reviewed_at"] = df["reviewed_at"].dt.tz_localize("UTC")
    df = df[COLUMNS].astype(object).where(df[COLUMNS].notna(), None)
    records = df.to_dict("records")
    for r in records:
        r["reviewed_at"] = r["reviewed_at"].to_pydatetime()
    return records


def status_counts(conn, app_id: int) -> dict[str, int]:
    return {status: int(n) for status, n in conn.execute(STATUS_COUNTS, {"a": app_id}).all()}


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", help="path file .parquet hasil scrape.py atau refilter_snapshot.py")
    p.add_argument("--app", default=os.getenv("TARGET_APP_PACKAGE", "com.whatsapp"))
    p.add_argument("--app-name", default="WhatsApp")
    p.add_argument(
        "--refresh-filter",
        action="store_true",
        help="perbarui lang dan exclude_reason ulasan yang sudah ada di database",
    )
    args = p.parse_args()

    url = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
    if not url:
        p.error("Set DATABASE_URL_LOCAL di .env")
    if "@db:" in url:
        p.error("Dari Ubuntu pakai DATABASE_URL_LOCAL (host localhost), bukan host 'db'")

    records = read_records(args.file)
    versions = sorted({r["app_version"] for r in records if r["app_version"]})

    engine = create_engine(url)
    with engine.begin() as conn:
        app_id = conn.execute(INSERT_APP, {"pkg": args.app, "name": args.app_name}).scalar_one()
        before = status_counts(conn, app_id)

        if args.refresh_filter:
            for i in range(0, len(records), CHUNK):
                chunk = [
                    {
                        "app_id": app_id,
                        "external_id": r["external_id"],
                        "lang": r["lang"],
                        "exclude_reason": r["exclude_reason"],
                    }
                    for r in records[i : i + CHUNK]
                ]
                conn.execute(UPDATE_FILTER, chunk)
        else:
            if versions:
                conn.execute(INSERT_VERSION, [{"app_id": app_id, "v": v} for v in versions])
            for i in range(0, len(records), CHUNK):
                chunk = [{**r, "app_id": app_id} for r in records[i : i + CHUNK]]
                conn.execute(INSERT_REVIEW, chunk)

        after = status_counts(conn, app_id)

    total_before, total_after = sum(before.values()), sum(after.values())
    print(f"Di file: {len(records)} | di DB sebelum: {total_before} | sesudah: {total_after}")
    print("Status sebelum:", before)
    print("Status sesudah:", after)
    if args.refresh_filter and len(records) != total_after:
        print("PERINGATAN: jumlah baris file berbeda dari jumlah baris di database.")


if __name__ == "__main__":
    main()
