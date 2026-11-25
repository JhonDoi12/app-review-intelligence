import csv
from functools import lru_cache
from pathlib import Path

SLANG_PATH = Path(__file__).with_name("slang_dict.csv")


@lru_cache(maxsize=1)
def load_slang(path: Path = SLANG_PATH) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as f:
        return {row["slang"]: row["formal"] for row in csv.DictReader(f)}


def normalize_slang(text: str, mapping: dict[str, str] | None = None) -> str:
    mapping = mapping or load_slang()
    return " ".join(mapping.get(token, token) for token in text.split())
