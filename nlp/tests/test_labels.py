import pytest

from review_nlp.sentiment.labels import rating_to_label


def test_tiga_kelas():
    labels = [rating_to_label(r) for r in (1, 2, 3, 4, 5)]
    assert labels == ["negatif", "negatif", "netral", "positif", "positif"]


def test_dua_kelas_membuang_bintang_tiga():
    assert rating_to_label(3, three_class=False) is None


def test_rating_tidak_valid():
    with pytest.raises(ValueError):
        rating_to_label(6)
