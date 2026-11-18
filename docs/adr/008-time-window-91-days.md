## Pembaruan (2026-11-18): pemilihan acak, bukan terbaru

Implementasi awal mengambil 800 ulasan **terbaru** tiap minggu. Karena volume harian
WhatsApp sekitar 650-800 ulasan, kuota habis oleh satu atau dua hari terakhir tiap
minggu (hasil: hanya 14 tanggal berbeda dari 91 hari). Sekarang scraper membaca seluruh
ulasan dalam jendela dan memilih maksimal 800 per minggu secara **acak** (reservoir
sampling, seed 42). Volume asli per minggu disimpan di berkas `*_weekly_volume.csv`.