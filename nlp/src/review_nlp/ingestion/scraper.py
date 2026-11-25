import logging
import random
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date

from google_play_scraper import Sort, reviews

log = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    rows: list[dict]
    seen_per_week: dict[int, int]  # volume asli per minggu, sebelum kuota


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
    seed: int = 42,
) -> ScrapeResult:
    """Baca semua ulasan di jendela waktu, lalu pilih acak maksimal `max_per_week`
    per minggu (reservoir sampling), sehingga seluruh hari dalam minggu terwakili."""
    rng = random.Random(seed)
    reservoirs: dict[int, list[dict]] = {}
    seen_per_week: Counter = Counter()
    seen_ids: set[str] = set()
    total_read = 0
    token = None

    while True:
        page, token = _fetch(app_id, lang, country, batch, token, sleep_s)
        if not page:
            break
        total_read += len(page)
        reached_start = False

        for row in page:
            d = row["at"].date()
            if d > until:
                continue
            if d < since:
                reached_start = True
                continue
            if row["reviewId"] in seen_ids:
                continue
            seen_ids.add(row["reviewId"])

            wk = week_index(d, since)
            seen_per_week[wk] += 1
            bucket = reservoirs.setdefault(wk, [])
            if len(bucket) < max_per_week:
                bucket.append(row)
            else:
                j = rng.randrange(seen_per_week[wk])
                if j < max_per_week:
                    bucket[j] = row

        log.info(
            "dibaca %d | unik dalam jendela %d | tanggal terlama di halaman: %s",
            total_read,
            len(seen_ids),
            page[-1]["at"].date(),
        )
        if reached_start or token is None:
            break
        time.sleep(sleep_s)

    rows = [row for wk in sorted(reservoirs) for row in reservoirs[wk]]
    return ScrapeResult(rows=rows, seen_per_week=dict(seen_per_week))
