from review_nlp.preprocessing import preprocess
from review_nlp.preprocessing.cleaner import clean_text


def test_lowercase_url_dan_emoji():
    assert clean_text("BAGUS banget 😍 https://wa.me/x") == "bagus banget"


def test_huruf_berulang():
    assert clean_text("bagusssss") == "bagus"


def test_angka_tidak_rusak():
    assert clean_text("versi 1000") == "versi 1000"


def test_placeholder_pii_dibuang():
    assert clean_text("hubungi [TELEPON] [EMAIL] sekarang") == "hubungi sekarang"


def test_slang_dinormalisasi():
    assert preprocess("gk bisa login") == "tidak bisa login"


def test_negasi_dipertahankan():
    assert "tidak" in preprocess("tidak bisa kirim pesan")


def test_huruf_gaya_unicode():
    assert clean_text("𝗴𝗮 𝗮𝗱𝗮 𝗲𝗳𝗲𝗸") == "ga ada efek"


def test_huruf_gaya_unicode_tetap_membawa_negasi():
    assert preprocess("𝗴𝗮 𝗮𝗱𝗮 𝗲𝗳𝗲𝗸") == "tidak ada efek"


def test_diakritik_dibuang():
    assert clean_text("café") == "cafe"
