import numpy as np
import pandas as pd
import pytest

from review_nlp.gold.sampling import allocate, dedupe_texts, stratified_sample

KUOTA = {1: 30, 2: 10, 3: 20}


def buat_populasi() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    baris = []
    for rating, jumlah in {1: 300, 2: 60, 3: 80}.items():
        for i in range(jumlah):
            baris.append(
                {
                    "external_id": f"r{rating}-{i:04d}",
                    "text_raw": f"teks {rating} {i}",
                    "rating": rating,
                    "week_index": int(rng.integers(0, 13)),
                }
            )
    return pd.DataFrame(baris)


def test_allocate_proporsional():
    counts = pd.Series({0: 10, 1: 20, 2: 30})
    assert allocate(counts, 12).to_dict() == {0: 2, 1: 4, 2: 6}


def test_allocate_sisa_ke_pecahan_terbesar():
    counts = pd.Series({0: 10, 1: 20, 2: 30})
    hasil = allocate(counts, 7)
    assert int(hasil.sum()) == 7
    assert hasil.to_dict() == {0: 1, 1: 2, 2: 4}


def test_allocate_kuota_melebihi_isi():
    counts = pd.Series({0: 3, 1: 2})
    assert allocate(counts, 10).to_dict() == {0: 3, 1: 2}


def test_sampel_sesuai_kuota_dan_bobot():
    sampel = stratified_sample(buat_populasi(), KUOTA, seed=1)
    assert sampel.groupby("rating").size().to_dict() == KUOTA
    assert sampel["external_id"].is_unique
    satu = sampel[sampel["rating"] == 1].iloc[0]
    assert satu["bobot"] == pytest.approx(10.0)
    assert satu["peluang_terpilih"] == pytest.approx(0.1)


def test_sampel_tersebar_proporsional_antar_minggu():
    populasi = buat_populasi()
    sampel = stratified_sample(populasi, KUOTA, seed=2)
    pop = populasi[populasi["rating"] == 1].groupby("week_index").size()
    sam = sampel[sampel["rating"] == 1].groupby("week_index").size()
    sam = sam.reindex(pop.index, fill_value=0)
    harapan = pop * 30 / pop.sum()
    assert ((sam - harapan).abs() <= 1).all()


def test_seed_sama_hasil_sama():
    populasi = buat_populasi()
    a = stratified_sample(populasi, KUOTA, seed=3)
    b = stratified_sample(populasi, KUOTA, seed=3)
    c = stratified_sample(populasi, KUOTA, seed=4)
    assert a["external_id"].tolist() == b["external_id"].tolist()
    assert a["external_id"].tolist() != c["external_id"].tolist()


def test_kuota_melebihi_populasi_ditolak():
    with pytest.raises(ValueError):
        stratified_sample(buat_populasi(), {2: 100}, seed=1)


def test_dedupe_teks_mengabaikan_huruf_besar_dan_spasi():
    df = pd.DataFrame(
        {
            "external_id": ["a", "b", "c"],
            "text_raw": ["Bagus  sekali", "bagus sekali", "jelek"],
        }
    )
    hasil = dedupe_texts(df)
    assert hasil["external_id"].tolist() == ["a", "c"]
