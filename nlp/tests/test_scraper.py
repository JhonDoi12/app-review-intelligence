from datetime import date, datetime

from review_nlp.ingestion import scraper

SINCE = date(2026, 8, 19)
UNTIL = date(2026, 11, 17)


def make_row(rid: str, d: date) -> dict:
    return {"reviewId": rid, "at": datetime(d.year, d.month, d.day, 12, 0)}


ROWS = [  # urut terbaru ke terlama, seperti Play Store
    make_row("r1", date(2026, 11, 20)),  # setelah until -> dilewati
    make_row("r2", date(2026, 11, 17)),
    make_row("r3", date(2026, 11, 16)),
    make_row("r4", date(2026, 11, 15)),
    make_row("r5", date(2026, 8, 20)),
    make_row("r6", date(2026, 8, 10)),  # sebelum since -> berhenti
]


def fake_reviews(app_id, lang, country, sort, count, continuation_token=None):
    start = continuation_token or 0
    nxt = start + 3
    return ROWS[start:nxt], (nxt if nxt < len(ROWS) else None)


def run(monkeypatch, max_per_week, seed=42):
    monkeypatch.setattr(scraper, "reviews", fake_reviews)
    return scraper.scrape_window(
        "x", since=SINCE, until=UNTIL, max_per_week=max_per_week, sleep_s=0, batch=3, seed=seed
    )


def test_jendela_tanpa_kuota(monkeypatch):
    result = run(monkeypatch, max_per_week=10)
    assert {r["reviewId"] for r in result.rows} == {"r2", "r3", "r4", "r5"}
    assert result.seen_per_week == {12: 3, 0: 1}


def test_kuota_mingguan_memilih_acak(monkeypatch):
    result = run(monkeypatch, max_per_week=2)
    ids = {r["reviewId"] for r in result.rows}
    assert len(ids) == 3
    assert "r5" in ids
    assert ids - {"r5"} <= {"r2", "r3", "r4"}
    assert result.seen_per_week[12] == 3  # volume asli tetap tercatat


def test_seed_sama_hasil_sama(monkeypatch):
    a = run(monkeypatch, max_per_week=2, seed=7)
    b = run(monkeypatch, max_per_week=2, seed=7)
    assert [r["reviewId"] for r in a.rows] == [r["reviewId"] for r in b.rows]
