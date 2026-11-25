from review_nlp.preprocessing.cleaner import clean_text
from review_nlp.preprocessing.slang_normalizer import normalize_slang


def preprocess(text: str) -> str:
    return normalize_slang(clean_text(text))


__all__ = ["clean_text", "normalize_slang", "preprocess"]
