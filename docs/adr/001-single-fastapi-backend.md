# ADR 001: Backend tunggal FastAPI

- **Status:** Diterima
- **Tanggal:** 2026-11-16

## Konteks
Rencana awal memakai Node.js untuk API utama dan FastAPI khusus NLP.
Dua service menambah kompleksitas tanpa nilai tambah jelas pada v1.

## Keputusan
Gunakan FastAPI sebagai satu-satunya backend. Next.js memanggilnya langsung.

## Konsekuensi
- Kode NLP dan API berbagi bahasa dan paket (`review_nlp`).
- Tidak ada Node API di v1; dapat ditambahkan di v2 jika ada kebutuhan jelas.