from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class SentimentResult:
    label: str  # "negatif" | "netral" | "positif"
    score: float  # keyakinan model, 0..1


class SentimentClassifier(ABC):
    name: str

    @abstractmethod
    def predict(self, texts: Sequence[str]) -> list[SentimentResult]: ...

    @abstractmethod
    def load(self, path_or_repo: str) -> None: ...