import pandas as pd

from review_nlp.gold.export import HEADER, tulis_xlsx


def test_xlsx_dapat_dibaca_kembali(tmp_path):
    sampel = pd.DataFrame({"id": [1, 2], "text_raw": ["bagus sekali", "jelek \x07 sekali"]})
    path = tmp_path / "label.xlsx"
    tulis_xlsx(path, sampel)
    hasil = pd.read_excel(path)
    assert hasil.columns.tolist() == HEADER
    assert hasil["tipe"].tolist() == ["biasa", "biasa"]
    assert hasil["label"].isna().all()
    assert "\x07" not in hasil.loc[1, "teks"]
