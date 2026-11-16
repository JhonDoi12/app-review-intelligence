# App Review Intelligence

Dashboard analisis sentimen dan topik keluhan dari ulasan Google Play Store
(studi kasus: WhatsApp), lengkap dengan tren per versi aplikasi.

> **Status:** dalam pengembangan (Fase 0: fondasi).
>
> **Penafian:** proyek ini adalah analisis ulasan publik untuk portofolio dan
> tidak berafiliasi dengan WhatsApp atau Meta. Identitas pengguna di-hash
> sebelum disimpan.

## Fitur yang direncanakan
- Scraping ulasan terjadwal, anonimisasi, dan filter bahasa
- Klasifikasi sentimen (TF-IDF + Logistic Regression vs IndoBERT)
- Topic modeling keluhan (BERTopic)
- Dashboard: tren sentimen, perbandingan versi, word cloud, penjelajah ulasan

## Arsitektur
Lihat [docs/architecture.md](docs/architecture.md) dan [docs/PRD.md](docs/PRD.md).

## Menjalankan secara lokal
```bash
cp .env.example .env     # isi nilai rahasia
make up                  # db + api + web
```
- API: http://localhost:8000/api/v1/health
- Web: http://localhost:3000

## Struktur
`nlp/` paket NLP · `api/` FastAPI · `web/` Next.js · `notebooks/` riset ·
`docs/` dokumentasi · `infra/` konfigurasi infrastruktur

## Hasil model
_Akan diisi setelah fase riset (perbandingan macro-F1 baseline vs IndoBERT)._