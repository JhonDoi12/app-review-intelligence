"""Ambil sampel gold set berstrata dan tulis berkas pelabelan (bintang disembunyikan)."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from review_nlp.gold.export import tulis_xlsx
from review_nlp.gold.sampling import QUOTAS, dedupe_texts, stratified_sample
from review_nlp.preprocessing import preprocess

KEY_COLUMNS = [
    "id",
    "external_id",
    "rating",
    "week_index",
    "app_version",
    "peluang_terpilih",
    "bobot",
]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", help="path snapshot v2 (.parquet)")
    p.add_argument("--out-dir", default="data/gold")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    xlsx = out_dir / "gold_to_label.xlsx"
    if xlsx.exists():
        p.error(f"{xlsx} sudah ada. Pindahkan dulu supaya label tidak tertimpa")

    df = pd.read_parquet(args.file)
    df = df[df["exclude_reason"].isna()]
    df = df[df["text_raw"].map(preprocess).str.len() > 0]
    populasi = dedupe_texts(df)
    sampel = stratified_sample(populasi, QUOTAS, seed=args.seed)
    sampel.insert(0, "id", range(1, len(sampel) + 1))

    out_dir.mkdir(parents=True, exist_ok=True)
    tulis_xlsx(xlsx, sampel)
    sampel[KEY_COLUMNS].to_csv(out_dir / "gold_key.csv", index=False)

    laporan = {
        "sumber": Path(args.file).name,
        "dibuat": datetime.now(UTC).isoformat(timespec="seconds"),
        "seed": args.seed,
        "kuota": QUOTAS,
        "total": len(sampel),
        "teks_duplikat_dibuang": int(len(df) - len(populasi)),
        "populasi_per_bintang": {
            int(k): int(v) for k, v in populasi["rating"].value_counts().sort_index().items()
        },
    }
    (out_dir / "gold_sampling_report.json").write_text(
        json.dumps(laporan, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    ringkas = (
        sampel.groupby("rating")
        .agg(kuota=("id", "size"), bobot=("bobot", "first"))
        .join(populasi.groupby("rating").size().rename("populasi"))
    )
    print(ringkas[["populasi", "kuota", "bobot"]].round(2).to_string())
    print(f"\nTotal: {len(sampel)} | duplikat dibuang: {laporan['teks_duplikat_dibuang']}")
    print(f"Lembar pelabelan: {xlsx}")
    print(f"Kunci (JANGAN dibuka sebelum selesai melabeli): {out_dir / 'gold_key.csv'}")


if __name__ == "__main__":
    main()
