import pandas as pd

from review_nlp.ingestion.transform import refilter


def test_refilter_menghitung_ulang_tanpa_mengubah_data_asli():
    df = pd.DataFrame({"text_raw": ["bagus"], "lang": ["x"], "exclude_reason": [None]})
    out = refilter(df)
    assert out.loc[0, "exclude_reason"] == "too_short"
    assert df.loc[0, "exclude_reason"] is None
