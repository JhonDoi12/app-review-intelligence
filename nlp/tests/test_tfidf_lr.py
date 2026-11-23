from review_nlp.sentiment.tfidf_lr import TfidfLrClassifier


def test_fit_dan_predict_data_kecil():
    positif = [
        "aplikasi bagus sekali",
        "bagus dan cepat",
        "sangat bagus",
        "bagus banget deh",
    ]
    negatif = [
        "tidak bisa login",
        "sering error parah",
        "tidak bisa kirim pesan",
        "error terus menerus",
    ]
    texts = (positif + negatif) * 3  # min_df=3 membutuhkan kata muncul di >= 3 dokumen
    labels = (["positif"] * 4 + ["negatif"] * 4) * 3

    clf = TfidfLrClassifier().fit(texts, labels)
    hasil = clf.predict(["aplikasi bagus sekali", "tidak bisa login"])

    assert [r.label for r in hasil] == ["positif", "negatif"]
    assert all(0.0 <= r.score <= 1.0 for r in hasil)