# ADR 009: Snapshot v2 setelah perbaikan filter bahasa

- **Status:** Diterima
- **Tanggal:** 2026-11-24

## Konteks
Filter bahasa awal menandai terlalu banyak ulasan Indonesia sebagai bahasa asing
(sekitar separuh dari 50 contoh yang diperiksa; teks KAPITAL terbaca sebagai bahasa
Jerman, dan ulasan campuran Inggris-Indonesia ikut terbuang). Ulasan yang terbuang
condong bernada keluhan. Filter diperbaiki: deteksi memakai huruf kecil, dan teks yang
memuat kata penanda Indonesia tidak dianggap bahasa asing.

## Keputusan
- Snapshot asli (v1) tidak diubah.
- Snapshot v2 dihitung ulang dari `text_raw` dengan filter final (`refilter`), tanpa
  scraping ulang, dan ringkasan parameternya disimpan sebagai berkas JSON.
- Kolom `lang` dan `exclude_reason` di database diperbarui dari v2
  (`load_to_db.py --refresh-filter`).
- Gold set dan semua evaluasi berikutnya memakai data v2.
- Setiap perubahan filter pada data yang sudah dikumpulkan harus menghasilkan versi
  snapshot baru dan ADR baru.

## Konsekuensi
- Angka pada notebook 01-03 (dihitung dengan `refilter`) konsisten dengan database.
- Deteksi bahasa tetap tidak sempurna untuk teks gaul/pendek; sekitar 10% dari contoh
  yang masih ditandai asing ternyata Indonesia atau campuran (dampak < 0,2% data).