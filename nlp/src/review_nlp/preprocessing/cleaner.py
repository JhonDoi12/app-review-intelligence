import re
import unicodedata

URL_RE = re.compile(r"https?://\S+|www\.\S+")
PLACEHOLDER_RE = re.compile(r"\[(?:email|telepon)\]")
EMOJI_RE = re.compile("[\U0001f000-\U0001faff\U00002600-\U000027bf\U0000fe0f\U0000200d]+")
REPEAT_RE = re.compile(r"([a-z])\1{2,}")  # 'bagusssss' -> 'bagus'
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")
SPACE_RE = re.compile(r"\s+")


def fold_unicode(text: str) -> str:
    """Ubah huruf bergaya (misalnya tebal atau full-width) menjadi huruf biasa
    dan buang tanda diakritik."""
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def clean_text(text: str) -> str:
    """Normalisasi Unicode, case folding, buang URL/penanda PII/emoji/tanda baca,
    rapikan huruf berulang."""
    text = fold_unicode(text).lower()
    text = URL_RE.sub(" ", text)
    text = PLACEHOLDER_RE.sub(" ", text)
    text = EMOJI_RE.sub(" ", text)
    text = REPEAT_RE.sub(r"\1", text)
    text = NON_ALNUM_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()
