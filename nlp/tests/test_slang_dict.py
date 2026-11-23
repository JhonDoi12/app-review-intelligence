import csv

from review_nlp.preprocessing.slang_normalizer import SLANG_PATH


def baca_baris():
    with SLANG_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_tidak_ada_kunci_ganda():
    kunci = [r["slang"] for r in baca_baris()]
    assert len(kunci) == len(set(kunci)), "ada kata slang ganda di slang_dict.csv"


def test_tidak_ada_spasi_di_tepi():
    for r in baca_baris():
        assert r["slang"] == r["slang"].strip()
        assert r["formal"] == r["formal"].strip()


def test_kunci_huruf_kecil_dan_tanpa_spasi():
    for r in baca_baris():
        assert r["slang"] == r["slang"].lower()
        assert " " not in r["slang"]


def test_tidak_memetakan_ke_diri_sendiri():
    for r in baca_baris():
        assert r["slang"] != r["formal"]
