import logging
import time
from collections import Counter
from datetime import date

from google_play_scraper import Sort, reviews

log = logging.getLogger(__name__)


def week_index(d: date, since: date) -> int:
    """Indeks minggu (0, 1, 2, ...) relatif terhadap tanggal awal jendela."""
    return (d - since).days // 7


def _fetch(app_id, lang, country, batch, token, sleep_s, retries=3):
    for attempt in range(1, retries + 1):
        try:
            return reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=batch,
                continuation_token=token,
            )
        except Exception as exc:  # pustaka tidak resmi: jenis error beragam
            if attempt == retries:
                raise
            wait = sleep_s * attempt * 2
            log.warning("Gagal mengambil halaman (%s). Coba lagi dalam %.1f detik", exc, wait)
            time.sleep(wait)


def scrape_window(
    app_id: str,
    since: date,
    until: date,
    lang: str = "id",
    country: str = "id",
    max_per_week: int = 800,
    sleep_s: float = 1.5,
    batch: int = 200,
) -> list[dict]:
    """Ambil ulasan terbaru-mundur sampai tanggal `since`, dengan kuota per minggu."""
    kept: list[dict] = []
    per_week: Counter = Counter()
    seen: set[str] = set()
    total_seen = 0
    token = None

    while True:
        page, token = _fetch(app_id, lang, country, batch, token, sleep_s)
        if not page:
            break
        total_seen += len(page)
        reached_start = False

        for row in page:
            d = row["at"].date()
            if d > until:
                continue
            if d < since:
                reached_start = True
                continue
            if row["reviewId"] in seen:
                continue
            wk = week_index(d, since)
            if per_week[wk] >= max_per_week:
                continue
            per_week[wk] += 1
            seen.add(row["reviewId"])
            kept.append(row)

        log.info(
            "dibaca %d | disimpan %d | tanggal terlama di halaman: %s",
            total_seen,
            len(kept),
            page[-1]["at"].date(),
        )
        if reached_start or token is None:
            break
        time.sleep(sleep_s)

    return kept
