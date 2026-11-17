import re

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0  # hasil deteksi deterministik

MIN_WORDS = 3
MIN_PROB = 0.90

# Hanya bahasa yang jelas bukan Indonesia. Bahasa serumpun/slang (ms, tl, dll.)
# sering salah terdeteksi untuk teks Indonesia, jadi sengaja tidak dibuang.
NON_ID_CLEAR = frozenset(
    {
        "en",
        "ar",
        "hi",
        "es",
        "pt",
        "fr",
        "de",
        "ru",
        "tr",
        "vi",
        "th",
        "ja",
        "ko",
        "zh-cn",
        "zh-tw",
        "ur",
        "bn",
        "fa",
    }
)

_WORD_RE = re.compile(r"\w+")


def detect_lang(text: str) -> tuple[str | None, float]:
    try:
        best = detect_langs(text)[0]
        return best.lang, float(best.prob)
    except LangDetectException:
        return None, 0.0


def analyze_text(
    text: str, min_words: int = MIN_WORDS, min_prob: float = MIN_PROB
) -> tuple[str | None, str | None]:
    """Kembalikan (kode_bahasa, alasan_eksklusi). Alasan None berarti ulasan dipakai."""
    if not text.strip():
        return None, "empty"
    lang, prob = detect_lang(text)
    if len(_WORD_RE.findall(text)) < min_words:
        return lang, "too_short"
    if lang in NON_ID_CLEAR and prob >= min_prob:
        return lang, "non_indonesian"
    return lang, None
