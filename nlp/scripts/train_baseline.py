"""Latih baseline TF-IDF + Logistic Regression dari snapshot Parquet."""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from review_nlp.ingestion.transform import refilter
from review_nlp.preprocessing import preprocess
from review_nlp.sentiment.evaluate import evaluate
from review_nlp.sentiment.labels import LABELS_3, rating_to_label
from review_nlp.sentiment.tfidf_lr import TfidfLrClassifier


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", help="path file .parquet")
    p.add_argument("--split", choices=["random", "temporal"], default="random")
    p.add_argument("--out", default="models/tfidf_lr.joblib")
    args = p.parse_args()

    df = pd.read_parquet(args.file)
    df = refilter(df)
    df = df[df["exclude_reason"].isna()].copy()
    df["label"] = df["rating"].map(rating_to_label)
    df["clean"] = df["text_raw"].map(preprocess)
    df = df[df["clean"].str.len() > 0]

    if args.split == "temporal":
        cutoff = df["week_index"].max() - 2  # 3 minggu terakhir untuk uji
        train, test = df[df["week_index"] <= cutoff], df[df["week_index"] > cutoff]
    else:
        train, test = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)

    clf = TfidfLrClassifier().fit(train["clean"], train["label"])
    pred = [r.label for r in clf.predict(test["clean"].tolist())]
    result = evaluate(test["label"], pred, LABELS_3)

    print(f"Split: {args.split} | latih: {len(train)} | uji: {len(test)}")
    print(f"Macro-F1 (label bintang, SEMENTARA): {result['macro_f1']:.4f}\n")
    print(result["report"])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    clf.save(str(out))
    print(f"Model disimpan: {out}")


if __name__ == "__main__":
    main()
