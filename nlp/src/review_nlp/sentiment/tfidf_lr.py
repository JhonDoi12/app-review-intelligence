from collections.abc import Sequence
from typing import Self

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from review_nlp.sentiment.base import SentimentClassifier, SentimentResult


class TfidfLrClassifier(SentimentClassifier):
    name = "tfidf_lr"

    def __init__(self, c: float = 1.0, seed: int = 42) -> None:
        tfidf = TfidfVectorizer(
            ngram_range=(1, 2), min_df=3, sublinear_tf=True, max_features=100_000
        )
        lr = LogisticRegression(C=c, class_weight="balanced", max_iter=1000, random_state=seed)
        self.pipeline = Pipeline([("tfidf", tfidf), ("lr", lr)])

    def fit(self, texts: Sequence[str], labels: Sequence[str]) -> Self:
        self.pipeline.fit(texts, labels)
        return self

    def predict(self, texts: Sequence[str]) -> list[SentimentResult]:
        proba = self.pipeline.predict_proba(texts)
        classes = self.pipeline.classes_
        return [
            SentimentResult(label=str(classes[row.argmax()]), score=float(row.max()))
            for row in proba
        ]

    def save(self, path: str) -> None:
        joblib.dump(self.pipeline, path)

    def load(self, path_or_repo: str) -> None:
        self.pipeline = joblib.load(path_or_repo)
