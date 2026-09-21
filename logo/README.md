# Logo UNNES untuk sampul

## Berkas di direktori ini

| Berkas | Isi |
|---|---|
| `logo-unnes.png` | Logo UNNES **hitam putih**: lambang, tulisan "UNNES", dan "UNIVERSITAS NEGERI SEMARANG"; latar transparan, 421 × 565 piksel (proporsi 1:1,34). **Dipakai sampul secara bawaan** (`logo=logo-unnes`) |
| `logo-unnes-warna.png` | Salinan asli berwarna dari berkas `Logo-Transparan-Warna-1.png` di akar repo (palet 5 warna, latar transparan, 1528 × 2037 piksel) — pakai `logo=logo-unnes-warna` bila sampul dicetak berwarna |
| `logo-placeholder.tex` dan `logo-placeholder.pdf` | Kotak penanda 1:1 berisi tulisan "UNNES" (bukan logo resmi) — hanya dipakai bila berkas logo tidak ditemukan |

Kelas memeriksa logo berurutan: `<logodir>/<logo>.pdf` (vektor, paling tajam), lalu `.png`, lalu
`.jpg`. Bila ketiganya tidak ada, halaman sampul memakai kotak placeholder dan menulis peringatan
di berkas `.log`.

## Cara logo hitam putih ini dibuat

Logo sumber di akar repo berwarna (emas pada lambang, merah pada nyala api, biru pada tulisan).
Skrip `skrip/siapkan-logo.py` mengubahnya menjadi hitam putih lalu menyimpannya di direktori ini:

```bash
cd ~/latex/unnes-ta
python3 skrip/siapkan-logo.py                  # sumber: Logo-Transparan-Warna-1.png
python3 skrip/siapkan-logo.py berkas-lain.png  # sumber lain
python3 skrip/siapkan-logo.py --faktor=2       # hasil lebih besar (kurang disusutkan)
```

Cara kerjanya: piksel yang jauh dari putih (emas, merah, biru) menjadi hitam, piksel putih logo
tetap putih, latar transparan tetap transparan; tepi transparan dipangkas, lalu gambar disusutkan
dengan rata-rata kotak (bawaan 1/3) supaya berkas kecil tetapi tepinya tetap halus saat dicetak.
Berkas sumber di akar repo boleh dihapus — salinannya ada di sini dan dipakai skrip sebagai sumber
cadangan.

## Baris "Universitas Negeri Semarang" di bawah logo

Logo bawaan sudah memuat tulisan "UNIVERSITAS NEGERI SEMARANG", sehingga baris tambahan di bawah
logo **dimatikan secara bawaan** (`namalogo=false`). Nyalakan bila memakai logo tanpa teks:

    \documentclass[namalogo=true]{unnes-ta}

## Hubungannya dengan aturan panduan

Panduan hal. 22, 35, 49, 64, 77 menuliskan: "Besarnya logo harus proporsional serta dengan
perbandingan ukuran P:L = 1:1 (dengan tanpa teks UNNES)". Logo bawaan template adalah logo lengkap
(lambang + tulisan "UNNES" + nama universitas) sesuai permintaan pemakaian, jadi secara harfiah
menyimpang dari bunyi panduan itu. Proporsinya tetap dijaga: opsi `ukuranlogo` (bawaan `3cm`)
menjadi batas sisi terpanjang logo, sehingga sampul memakai tinggi 3 cm dan lebar mengikuti
proporsi berkas (2,24 cm).

Bila ingin persis seperti bunyi panduan (lambang saja, persegi 1:1, tanpa teks), letakkan lambang
tersebut sebagai `logo/logo-unnes.pdf` atau `logo/logo-unnes.png` — kelas memakainya tanpa
perubahan kode.

## Mengganti dengan logo resmi

Letakkan logo resmi sebagai `logo/logo-unnes.pdf` (vektor paling tajam) atau
`logo/logo-unnes.png`; selama berkas `.pdf` ada, kelas memakainya dan mengabaikan `.png`. Untuk
sampul berwarna, pakai `logo=logo-unnes-warna`.
