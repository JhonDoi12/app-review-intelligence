import re

URL_RE = re.compile(r"https?://\S+|www\.\S+")
PLACEHOLDER_RE = re.compile(r"\[(?:email|telepon)\]")
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0000FE0F\U0000200D]+"
)
REPEAT_RE = re.compile(r"([a-z])\1{2,}")  # 'bagusssss' -> 'bagus'
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")
SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Case folding, buang URL/penanda PII/emoji/tanda baca, rapikan huruf berulang."""
    text = text.lower()
    text = URL_RE.sub(" ", text)
    text = PLACEHOLDER_RE.sub(" ", text)
    text = EMOJI_RE.sub(" ", text)
    text = REPEAT_RE.sub(r"\1", text)
    text = NON_ALNUM_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()