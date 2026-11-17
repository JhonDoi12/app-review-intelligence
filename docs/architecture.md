Arsitektur Enterprise

## 2.1 Prinsip

| Prinsip | Penerapan |
|---|---|
| Separation of concerns | Ingestion, NLP, API, dan UI dipisah per modul. |
| Reproducibility | Snapshot dataset, versi model tercatat, dan seed tetap. |
| Replaceable components | Model berada di balik antarmuka `SentimentClassifier`. |
| Lean first, scale later | Redis, Airflow, dan Node API masuk backlog v2. |
| Privacy by design | Identitas pengguna di-hash sebelum disimpan. |

## 2.2 Arsitektur Logis

```text
                     ┌───────────────────────────┐
                     │ Google Play (WhatsApp)  │
                     └─────────────┬─────────────┘
                                   │ google-play-scraper
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│ INGESTION (Python)                                         │
│ scraper → anonymizer → language filter → reviews (Postgres)│
│ dijadwalkan: GitHub Actions cron                           │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ NLP (Python)                                                │
│ preprocessing → sentiment classifier → topic model           │
│ (slang, Sastrawi)  (TF-IDF+LR | IndoBERT)  (BERTopic, neg.) │
│ hasil → review_predictions                                   │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ API (FastAPI + SQLAlchemy)                                  │
│ /summary /trends /versions /topics /reviews /predict /health│
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ WEB (Next.js + ECharts)                                      │
│ Overview · Versi · Topik · Ulasan · Uji Teks · Tentang Model│
└──────────────────────────────────────────────────────────────┘

PostgreSQL = data    |    Hugging Face Hub = artefak model
```

## 2.3 Lapisan dan Tanggung Jawab

| Lapisan | Teknologi | Tanggung jawab |
|---|---|---|
| Presentation | Next.js, TypeScript, ECharts, d3-cloud | Dashboard, filter, dan uji teks. |
| API | FastAPI, Pydantic, SQLAlchemy, Alembic | Kontrak data, agregasi, dan inferensi. |
| NLP | scikit-learn, transformers, BERTopic, Sastrawi | Preprocessing, sentimen, dan topik. |
| Ingestion | google-play-scraper, pandas | Scraping, deduplikasi, dan anonimisasi. |
| Data | PostgreSQL | Ulasan, prediksi, topik, versi, dan registry model. |
| Artefak | Hugging Face Hub | Model dan tokenizer. |
| DevOps | Docker Compose, GitHub Actions | Lingkungan lokal, CI, dan jadwal ingestion. |

## 2.4 Model Data

```sql
apps(
  id,
  package_name,
  name,
  created_at
)

app_versions(
  id,
  app_id,
  version_name,
  released_at
)

reviews(
  id,
  app_id,
  external_id UNIQUE,
  user_hash,
  rating,
  text_raw,
  thumbs_up,
  app_version,
  reviewed_at,
  scraped_at,
  lang
  exclude_reason
)

review_predictions(
  id,
  review_id,
  model_version_id,
  text_clean,
  sentiment,
  sentiment_score,
  topic_id NULL,
  predicted_at
)

topics(
  id,
  run_id,
  label,
  keywords[],
  size,
  created_at
)

model_versions(
  id,
  kind,
  name,
  hf_repo,
  metrics_json,
  is_active,
  created_at
)

gold_labels(
  id,
  review_id,
  label,
  annotator,
  created_at
)
```

Prediksi dipisah dari ulasan mentah agar model dapat diganti dan prediksi dapat diulang tanpa mengubah data asli.

## 2.5 Kontrak API v1

| Endpoint | Fungsi |
|---|---|
| `GET /api/v1/summary` | KPI ringkas. |
| `GET /api/v1/trends/sentiment?granularity=week` | Tren sentimen. |
| `GET /api/v1/versions/compare?v_a={v_a}&v_b={v_b}` | Perbandingan dua versi. |
| `GET /api/v1/topics` | Daftar topik. |
| `GET /api/v1/topics/{id}/wordcloud` | Frekuensi kata per topik. |
| `GET /api/v1/reviews` | Penjelajah dengan filter dan paginasi. |
| `GET /api/v1/reviews/most-negative` | Ulasan paling negatif. |
| `POST /api/v1/predict` | Uji teks manual. |
| `GET /api/v1/health` | Status layanan dan versi model aktif. |

### Catatan kontrak

- Endpoint daftar ulasan harus mendukung paginasi dan filter yang didefinisikan pada PRD.
- `/predict` perlu rate limit dan validasi panjang teks.
- Endpoint agregasi menargetkan waktu respons di bawah 500 ms.
- Bentuk request/response ditetapkan melalui schema Pydantic dan didokumentasikan (misalnya OpenAPI).

## 2.6 Keputusan Arsitektur (ADR)

| ADR | Keputusan | Alasan | Konsekuensi |
|---|---|---|---|
| 001 | Backend tunggal FastAPI | NLP dan API sama-sama Python. | Tanpa Node API di v1. |
| 002 | PostgreSQL | Agregasi tren dan join versi lebih natural. | Perlu migrasi Alembic. |
| 003 | Weak label + gold set manual | Hemat anotasi, tetap kredibel. | Metrik utama dihitung pada gold set. |
| 004 | Model di Hugging Face Hub | Repository tetap ringan. | Membutuhkan `download_model.py`. |
| 005 | Tanpa Redis di v1 | Beban awal kecil. | Redis ditambahkan di v2 bila performa menurun. |
| 006 | Cron via GitHub Actions | Gratis dan mudah disiapkan. | Runtime Actions terbatas. |
| 007 | Demo: data statis + inferensi ringan | Hosting model besar mahal. | Demo menggunakan snapshot. |
| 008 | Ambil ulasan pada jendela 19 Agustus sampai 17 November 2026 (91 hari = 13 minggu
penuh), maksimal 800 ulasan per minggu, sehingga total maksimal sekitar 10.400. | WhatsApp memiliki volume ulasan sangat besar. Untuk analisis sentimen, jumlah
dan keberagaman ulasan lebih penting daripada rentang waktu yang panjang. | Tren mingguan memiliki 13 titik data, Tidak ada klaim tren jangka panjang; model dilatih pada satu jendela waktu, Scraper membaca dari ulasan terbaru mundur, sehingga waktu scraping bergantung
  pada volume harian di jendela tersebut. |

## 2.7 Evolusi v2

Ruang pengembangan berikutnya:

- Redis untuk cache agregasi.
- Airflow atau Prefect untuk orkestrasi pipeline.
- Autentikasi dan multi-aplikasi.
- Alert lonjakan keluhan.
- Varian WhatsApp Business.
- Node/NestJS bila terdapat kebutuhan bisnis yang jelas.
