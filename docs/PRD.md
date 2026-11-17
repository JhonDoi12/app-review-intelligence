# Product Requirements Document (PRD)
## App Review Intelligence — WhatsApp

**Versi:** 1.0  
**Status:** Draft  
**Tanggal:** 2026-11-16

## 1.1 Ringkasan

App Review Intelligence adalah dashboard yang mengumpulkan ulasan Google Play Store, mengklasifikasikan sentimennya, mengekstrak topik keluhan utama, dan menampilkan tren berdasarkan waktu serta versi aplikasi.

Studi kasus v1: WhatsApp (`com.whatsapp`).

## 1.2 Latar Belakang dan Masalah

Tim produk kesulitan membaca ribuan ulasan secara manual. Akibatnya, tim sulit menjawab pertanyaan seperti:

- Keluhan apa yang paling mendesak setelah versi aplikasi tertentu dirilis?
- Bagaimana perubahan sentimen pengguna dari waktu ke waktu?
- Bug atau masalah pengalaman pengguna apa yang paling sering disebutkan?

## 1.3 Tujuan dan Metrik Keberhasilan

| Tujuan | Metrik | Target awal |
|---|---|---|
| Sentimen akurat | Macro-F1 pada gold set | ≥ 0,75 (IndoBERT); baseline tercatat |
| Topik bermakna | Topic coherence C_v dan penilaian manual | C_v ≥ 0,45; ≥ 80% topik utama terlabeli |
| Dashboard responsif | Waktu respons endpoint agregasi | < 500 ms |
| Reprodusibel | Setup dari nol | `docker compose up` + ≤ 5 perintah |
| Kualitas rekayasa | CI dan coverage inti NLP | PR hijau; coverage > 70% |

Target angka akan direvisi setelah fase riset.

## 1.4 Ruang Lingkup

### Termasuk (v1)

- Satu aplikasi: WhatsApp.
- Ulasan berbahasa Indonesia.
- Klasifikasi sentimen 3 kelas: negatif, netral, positif.
- Topic modeling pada ulasan negatif.
- Dashboard analitik.
- Pengujian sentimen teks manual.
- Scraping terjadwal.

### Tidak termasuk (v1)

- Multi-aplikasi atau multi-tenant.
- Autentikasi pengguna.
- Apple App Store.
- Alert real-time.
- Bahasa selain Indonesia.
- Redis, Airflow, dan Node API.

## 1.5 Pengguna

| Persona | Kebutuhan |
|---|---|
| Product Manager | Melihat apakah sentimen turun setelah update dan menemukan topik penyebabnya. |
| QA/Engineer | Menemukan ulasan yang menyebut bug spesifik beserta contoh teksnya. |
| Reviewer portofolio | Memahami proyek dalam 2 menit melalui demo dan README. |

## 1.6 Kebutuhan Fungsional

| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-01 | Scrape ulasan com.whatsapp (lang id, country id) pada jendela 91 hari dengan kuota 800 per minggu, tanpa duplikat (external_id). | Must |
| FR-02 | Hash nama/ID pengguna sebelum disimpan. | Must |
| FR-03 | Tandai (bukan hapus) ulasan kosong, kurang dari 3 kata, atau jelas bukan berbahasa Indonesia lewat kolom exclude_reason. | Must |
| FR-04 | Preprocessing: case folding, hapus URL/emoji, normalisasi slang, dan stopword removal. | Must |
| FR-05 | Weak labeling dari rating: 1–2 negatif, 3 netral, 4–5 positif. | Must |
| FR-06 | Klasifikasi sentimen 3 kelas dan evaluasi pada gold set manual. | Must |
| FR-07 | Topic modeling pada ulasan negatif dengan label topik manual. | Must |
| FR-08 | KPI ringkas: total ulasan, rata-rata rating, dan proporsi sentimen. | Must |
| FR-09 | Tren sentimen per minggu. | Must |
| FR-10 | Perbandingan rating dan sentimen sebelum/sesudah versi aplikasi. | Must |
| FR-11 | Daftar ulasan paling negatif. | Must |
| FR-12 | Penjelajah ulasan dengan filter topik, tanggal, rating, sentimen, dan pencarian teks. | Must |
| FR-13 | Word cloud per topik. | Should |
| FR-14 | Uji sentimen teks manual. | Should |
| FR-15 | Penanda ulasan yang rating bintangnya bertentangan dengan prediksi teks. | Could |
| FR-16 | Scraping terjadwal. | Should |
| FR-17 | Halaman “Tentang Model” (baseline vs IndoBERT dan keterbatasan weak label). | Should |

## 1.7 Kebutuhan Non-Fungsional

| Aspek | Target |
|---|---|
| Performa | Agregasi < 500 ms; `/predict` < 2 detik. |
| Reprodusibilitas | Seed tetap, snapshot dataset berversi, dan metrik tersimpan. |
| Kualitas kode | Ruff, mypy, ESLint, tsc; coverage inti > 70%. |
| Keamanan | `.env` tidak di-commit; identitas pengguna di-hash; rate limit `/predict`. |
| Observabilitas | Logging terstruktur dan endpoint `/health`. |
| UI | Responsif (laptop/HP), berbahasa Indonesia, dan kontras warna memadai. |

## 1.8 Pertimbangan Khusus Target WhatsApp

| Karakteristik | Dampak | Penanganan |
|---|---|---|
| Penanganan: “Jendela 91 hari + kuota per minggu, bukan sampel lintas bulan” | Sampel harus representatif. | Ambil sampel per rentang waktu (stratified by month), bukan hanya ulasan terbaru. |
| Banyak ulasan sangat pendek (“bagus”, “mantap”) | Informasi topik minim. | Filter minimal 3 kata; laporkan jumlah yang dibuang. |
| Bahasa campuran meski filter `id` | Noise bahasa. | Deteksi bahasa (`langdetect`/`fasttext`), buang non-Indonesia. |
| Topik keluhan khas: verifikasi/OTP, backup chat, akun diblokir, update tampilan, iklan di Status, privasi/kebijakan | Hipotesis awal topik. | Gunakan sebagai hipotesis awal BERTopic dan validasi dari data. |
| Bintang 5 dominan | Kelas tidak seimbang. | `class_weight=balanced`, stratified split, dan macro-F1. |
| Versi aplikasi tidak selalu terisi | Perbandingan versi bisa tidak lengkap. | Gunakan `reviewCreatedVersion`; jika kosong, gunakan tanggal rilis sebagai batas dan tandai estimasi. |

> **Penafian:** Proyek ini menganalisis ulasan publik untuk portofolio dan tidak berafiliasi dengan WhatsApp/Meta. Cantumkan penafian ini di README.

## 1.9 Metodologi

1. Sesuaikan dengan jendela 91 hari dan penandaan eksklusi.
2. Weak labeling dari rating; lakukan stratified split train/validation/test.
3. Buat gold set berisi 300–500 ulasan yang dilabeli manual (`labeling-guideline.md`).
4. Bangun baseline TF-IDF + Logistic Regression.
5. Fine-tune IndoBERT (Colab/Kaggle) dan simpan model ke HuggingFace Hub.
6. Bandingkan macro-F1 pada gold set; evaluasi skenario 3 kelas vs 2 kelas (tanpa rating bintang 3).
7. Jalankan BERTopic pada ulasan negatif; evaluasi coherence dan beri label topik secara manual.

## 1.10 Layar Dashboard

1. **Overview** — KPI utama dan ringkasan sentimen.
2. **Versi** — Perbandingan rating dan sentimen sebelum/sesudah versi.
3. **Topik** — Topik keluhan, jumlah ulasan, dan word cloud.
4. **Ulasan** — Penjelajah ulasan dengan filter dan pencarian.
5. **Uji Teks** — Prediksi sentimen dari teks yang dimasukkan manual.
6. **Tentang Model** — Penjelasan model, evaluasi, dan keterbatasan.

## 1.11 Risiko dan Mitigasi

| Risiko | Mitigasi |
|---|---|
| Scope creep | Fase bertahap dan backlog v2 yang tegas. |
| Label noisy | Gold set manual dan filter teks pendek. |
| Scraper terblokir | Snapshot dataset, jeda antar-request, dan demo statis. |
| Jendela pendek: tidak ada klaim tren jangka panjang | Sampling per bulan. |
| Topik tidak bermakna | Hanya ulasan negatif, tuning, dan label manual. |
| Hosting model berat | Demo statis dan inferensi ringan. |
| Data pribadi | Hash identitas dan cantumkan sumber data. |

## 1.12 Rencana Rilis

| Fase | Minggu | Keluaran | Selesai bila |
|---|---:|---|---|
| 0. Fondasi | 1 | Repo, CI, docker-compose, skema DB. | `docker compose up` berjalan dan CI hijau. |
| 1. Scraper + DB (A) | 1–2 | Scraper, anonymizer, snapshot. | 5.000+ ulasan tersimpan tanpa duplikat. |
| 2. EDA + Baseline (C) | 2–3 | Notebook 01–03 dan F1 awal. | Distribusi dan F1 baseline terdokumentasi. |
| 3. Gold set (B) | 3 | 300–500 label manual. | Metrik dihitung pada gold set. |
| 4. IndoBERT | 3–4 | Fine-tuning dan perbandingan. | Tabel macro-F1 tersedia di README. |
| 5. Topik | 4–5 | BERTopic dan label topik. | Topik utama terlabeli. |
| 6. API | 5–6 | Endpoint v1. | Semua endpoint lulus tes. |
| 7. Dashboard | 7–8 | UI, README, dan demo. | Demo hidup dan README lengkap. |

## 1.13 Definition of Done

Proyek dinyatakan selesai jika:

- README memuat masalah, arsitektur, hasil F1, keterbatasan weak label, screenshot, dan panduan menjalankan.
- CI hijau di branch `main`.
- Model tersedia di HuggingFace Hub.
- Tidak ada file besar yang disimpan di Git.
- Demo dapat diakses.
