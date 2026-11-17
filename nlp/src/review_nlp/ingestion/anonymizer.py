import hashlib
import hmac
import re

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?62|0)[\s-]?8\d{1,3}[\s-]?\d{3,4}[\s-]?\d{2,5}(?!\d)")


def hash_user(value: str, salt: str) -> str:
    """Pseudonimisasi nama pengguna dengan HMAC-SHA256 (deterministik per salt)."""
    if not salt:
        raise ValueError("salt tidak boleh kosong")
    return hmac.new(salt.encode(), value.encode(), hashlib.sha256).hexdigest()


def mask_pii(text: str) -> str:
    """Ganti email dan nomor telepon di dalam teks ulasan dengan penanda."""
    text = EMAIL_RE.sub("[EMAIL]", text)
    return PHONE_RE.sub("[TELEPON]", text)
