# ADR 008: Jendela data 91 hari dengan kuota per minggu

- **Status:** Diterima (menggantikan rencana "sampling per bulan")
- **Tanggal:** 2026-11-17

## Konteks
WhatsApp memiliki volume ulasan sangat besar. Untuk analisis sentimen, jumlah
dan keberagaman ulasan lebih penting daripada rentang waktu yang panjang.

## Keputusan
Ambil ulasan pada jendela 19 Agustus sampai 17 November 2026 (91 hari = 13 minggu
penuh), maksimal 800 ulasan per minggu, sehingga total maksimal sekitar 10.400.

## Konsekuensi
- Tren mingguan memiliki 13 titik data.
- Tidak ada klaim tren jangka panjang; model dilatih pada satu jendela waktu.
- Scraper membaca dari ulasan terbaru mundur, sehingga waktu scraping bergantung
  pada volume harian di jendela tersebut.