from review_nlp.ingestion.lang_filter import analyze_text, detect_lang


def test_kosong():
    assert analyze_text("   ") == (None, "empty")


def test_terlalu_pendek():
    _, reason = analyze_text("bagus banget")
    assert reason == "too_short"


def test_bahasa_inggris_ditandai():
    _, reason = analyze_text("this application keeps crashing every time I open it")
    assert reason == "non_indonesian"


def test_indonesia_dipakai():
    _, reason = analyze_text("aplikasinya sering error saat saya mencoba login")
    assert reason is None


def test_deteksi_tidak_bergantung_huruf_besar():
    teks = "KENAPA WHATSAPP SAYA SERING KEBLOKIR PADAHAL TIDAK NGAPA NGAPAIN"
    assert detect_lang(teks) == detect_lang(teks.lower())


def test_campuran_inggris_indonesia_dipakai():
    _, reason = analyze_text("Very Good. Tapi memory hp boros banget")
    assert reason is None
