from datetime import date, datetime

from review_nlp.ingestion import scraper


def make_row(rid: str, d: date) -> dict:
    return {"reviewId": rid, "at": datetime(d.year, d.month, d.day, 12, 0)}


def test_jendela_dan_kuota_mingguan(monkeypatch):
    rows = [  # urut terbaru ke terlama, seperti Play Store
        make_row("r1", date(2026, 11, 20)),  # setelah until -> dilewati
        make_row("r2", date(2026, 11, 17)),
        make_row("r3", date(2026, 11, 16)),
        make_row("r4", date(2026, 11, 15)),  # minggu penuh (kuota 2) -> ditolak
        make_row("r5", date(2026, 8, 20)),
        make_row("r6", date(2026, 8, 10)),  # sebelum since -> berhenti
    ]

    def fake_reviews(app_id, lang, country, sort, count, continuation_token=None):
        start = continuation_token or 0
        nxt = start + 3
        return rows[start:nxt], (nxt if nxt < len(rows) else None)

    monkeypatch.setattr(scraper, "reviews", fake_reviews)

    kept = scraper.scrape_window(
        "x",
        since=date(2026, 8, 19),
        until=date(2026, 11, 17),
        max_per_week=2,
        sleep_s=0,
        batch=3,
    )
    assert [r["reviewId"] for r in kept] == ["r2", "r3", "r5"]
