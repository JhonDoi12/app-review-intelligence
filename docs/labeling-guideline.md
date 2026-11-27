# Panduan Pelabelan Gold Set

**Versi:** 1.0 | **Tanggal:** 2026-11-26 | **Pelabel:** penulis (satu orang)

## 1. Tujuan
Membuat label sentimen berdasarkan **isi teks** sebagai kebenaran dasar untuk (1) mengukur
kualitas model dan (2) mengukur seberapa noisy label bintang. Bintang **disembunyikan**
selama pelabelan.

## 2. Pertanyaan utama
> Bagaimana sikap penulis terhadap WhatsApp (aplikasi, layanan, atau pengalaman memakainya)
> yang tersirat dalam teks ini?

Yang dinilai adalah **sikap**, bukan topik, tata bahasa, atau benar-tidaknya keluhan.

## 3. Tiga label
| Label | Definisi | Contoh (rekaan) |
|---|---|---|
| **positif** | Puas, memuji, berterima kasih, atau merekomendasikan | "Chat lancar, video call jernih, sangat membantu kerja saya" |
| **negatif** | Mengeluh, kecewa, melaporkan masalah, mengkritik, atau mengancam pindah | "Akun diblokir tanpa alasan, banding tidak dibalas" |
| **netral** | Tidak menilai: fakta, pertanyaan informasi, saran tanpa nada, atau tidak relevan | "Bagaimana cara memindahkan chat ke HP baru?" |

## 4. Aturan kasus sulit
| Kasus | Label | tipe |
|---|---|---|
| Saran atau permintaan fitur tanpa nada kecewa atau senang ("Tolong tambah jadwal kirim pesan") | netral | saran |
| Saran dengan nada kecewa ("Masa fitur segini belum ada, ketinggalan jauh") | negatif | saran |
| Saran disertai pujian ("Sudah bagus, semoga ada fitur X") | positif | saran |
| Pertanyaan informasi ("Cara backup chat bagaimana?") | netral | pertanyaan |
| Pertanyaan yang sebenarnya keluhan ("Kenapa akun saya diblokir terus?") | negatif | pertanyaan |
| Laporan masalah tanpa emosi ("Notifikasi tidak muncul sejak update") | negatif | biasa |
| Pujian dan keluhan sekaligus | Pilih **kesan keseluruhan** (penekanan, kata penutup, bagian setelah "tapi" sebagai pemberat). Kalau seimbang dan tidak bisa memilih dalam sekitar 5 detik: **netral** | campuran |
| Sarkasme atau ironi | Label sesuai **makna yang dimaksud**; kalau tidak yakin, centang `ragu` | biasa |
| Kata kasar ditujukan ke WhatsApp atau Meta | negatif | biasa |
| "Dulu bagus, sekarang jelek" | negatif (keadaan sekarang) | biasa |
| Ancaman pindah aplikasi | negatif | biasa |
| Cerita kronologis tanpa penilaian | netral | biasa |
| Peringatan soal penipu atau orang lain, tanpa menyalahkan aplikasi | netral | biasa |
| Menyalahkan aplikasi karena penipuan atau tidak aman | negatif | biasa |
| Spam, iklan, judi, atau tidak berhubungan dengan WhatsApp | netral | spam |
| Terpotong, gibberish, tidak bisa dipahami | netral (centang `ragu`) | tidak_jelas |
| Campuran bahasa Inggris atau daerah | Dilabeli seperti biasa | biasa |
| Emoji | Pertimbangkan bila teks pendek atau ambigu. Emoji bertentangan dengan teks: centang `ragu` | biasa |

## 5. Kolom lembar pelabelan
- **label** (wajib): `negatif`, `netral`, atau `positif` (dropdown).
- **tipe** (sudah terisi `biasa`): ubah hanya bila kasusnya `saran`, `pertanyaan`, `campuran`,
  `spam`, atau `tidak_jelas`.
- **ragu**: isi `y` bila setelah sekitar 10 detik masih bimbang antara dua label. Label **tetap
  wajib diisi** dengan pilihan terbaik.
- **catatan**: bebas. Tulis kata slang yang tidak dimengerti (`slang: xyz`).

## 6. Cara bekerja
1. Satu sesi **60-90 menit** (sekitar 100-150 ulasan), dengan jeda. Berhenti bila lelah.
2. **Jangan membuka `gold_key.csv`**, jangan mencari bintang, dan jangan memakai prediksi model.
3. Putuskan cepat (sekitar 10-15 detik per ulasan). Jangan mencari arti kata di internet
   terlalu lama; catat di `catatan`.
4. Jangan mengubah aturan di tengah jalan. Kasus yang belum tercakup: putuskan, catat di
   **Log keputusan** (nomor id, tanggal, keputusan), dan terapkan ke ulasan berikutnya.
   Setelah semua selesai, tinjau ulang ulasan sebelumnya yang terkait.
5. Simpan sering. Satu berkas saja, jangan membuat salinan.

## 7. Cek konsistensi
Setelah minimal 3 hari, 50 ulasan acak dilabeli ulang (putaran 2) tanpa melihat label
sebelumnya. Kesepakatan diukur dengan Cohen's kappa dan dilaporkan di README.

## 8. Keterbatasan
Satu pelabel, subjektivitas pada kasus campuran dan sarkasme, dan ukuran 450 ulasan.

## 9. Log keputusan
| Tanggal | id | Keputusan |
|---|---|---|
| | | |