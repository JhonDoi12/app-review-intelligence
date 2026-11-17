import pytest

from review_nlp.ingestion.anonymizer import hash_user, mask_pii


def test_hash_deterministik():
    assert hash_user("budi", "garam") == hash_user("budi", "garam")


def test_hash_berbeda_untuk_salt_berbeda():
    assert hash_user("budi", "a") != hash_user("budi", "b")


def test_hash_tidak_memuat_nama_asli():
    assert "budi" not in hash_user("budi", "garam")


def test_salt_kosong_ditolak():
    with pytest.raises(ValueError):
        hash_user("budi", "")


def test_mask_email_dan_telepon():
    masked = mask_pii("hubungi budi@mail.com atau 081234567890 / +62 812-3456-7890")
    assert "@" not in masked
    assert "0812" not in masked
    assert "[EMAIL]" in masked
    assert masked.count("[TELEPON]") == 2
