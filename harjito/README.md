# Contoh dokumen

Setiap direktori di sini adalah satu dokumen tugas akhir yang utuh dan sudah bisa dikompilasi.
Salin direktorinya lewat `../skrip/salin-dokumen.py` (rujukan berjalur relatif dibereskan otomatis),
ubah datanya, lalu tuliskan isi babnya. Seluruh dokumen di direktori ini dikompilasi serentak
dengan `../skrip/build.sh harjito` dari akar repo, satu dokumen dengan `./kompilasi.sh` di dalam
direktorinya, dan di code-server/VS Code cukup menekan Ctrl+S (setelan ada di
`.vscode/settings.json` tiap direktori).

## Data identitas: satu berkas untuk semua contoh

`identitas.tex` di direktori ini adalah **satu-satunya** berkas data identitas: nama, NIM, prodi,
fakultas, pembimbing, tim penguji, dan biodata penulis. Setiap dokumen mengambilnya dengan
`\input{../identitas}` di `main.tex`, lalu menambahkan kunci yang khusus dokumen itu (judul, gelar,
pembimbing kedua). Mengubah nama pembimbing cukup sekali di `contoh/identitas.tex` dan seluruh
contoh proposal/laporan/repositori ikut berubah.

```
contoh/
  identitas.tex            data identitas semua contoh (satu-satunya berkas identitas)
  skripsi-laporan/
    main.tex               kelas, \input{../identitas} + judul dokumen, urutan bab dan lampiran
    bab/01-pendahuluan.tex, 02-kajian-pustaka.tex, ...   isi tiap bab
    lampiran/01-instrumen-penelitian.tex, ...            isi tiap lampiran
    gambar/diagram-alur.pdf                              gambar dokumen ini
    .vscode/settings.json  jalur %DIR% ke akar repo (portabel) + build saat simpan
```

Berkas `.vscode/settings.json` dibuat oleh `../skrip/siapkan-vscode.py`. Isinya menyetel
LaTeX Workshop (code-server/VS Code) supaya kelas `unnes-ta.cls`, paket `unnes-ta-*.sty`, berkas
gaya `bst/`, pustaka `referensi/`, dan logo di akar repo terjangkau walaupun `main.tex` disunting
dari dalam subdirektori: menekan Ctrl+S langsung mengompilasi ulang
(pdflatex → bibtex → pdflatex → pdflatex) dan memperbarui `main.pdf`.

Jalurnya ditulis lewat placeholder `%DIR%` (diisi LaTeX Workshop saat resep dijalankan) dan
`$TEXMFDIST` (dikembangkan kpathsea), bukan jalur absolut PC tempat skrip itu dijalankan. Jadi
setelan ini tetap benar setelah repo dipindah ke PC lain, dengan nama pengguna maupun letak home
yang berbeda — cukup salin repositorinya, tanpa menjalankan ulang skrip apa pun.

Menambah bab atau lampiran: buat berkasnya di `bab/` atau `lampiran/`, lalu tambahkan satu baris
`\input{bab/NN-nama}` atau `\input{lampiran/NN-nama}` di `main.tex` pada urutan yang dikehendaki.
Gambar dokumen diletakkan di `gambar/` dan dipakai dengan
`\includegraphics[width=8cm]{gambar/nama-berkas}`.

| Direktori | Jenis, mode, jenjang | Bagian utama |
|---|---|---|
| `skripsi-laporan` | skripsi, laporan, sarjana, APA | bab 1-5, dua pembimbing, tabel + gambar |
| `skripsi-proposal` | skripsi, proposal, sarjana, APA | bab 1-3, tanpa pengesahan/abstrak/prakata |
| `proyek-laporan` | proyek, laporan, sarjana, APA | bab 1-5, mitra kegiatan + lampirannya |
| `proyek-proposal` | proyek, proposal, sarjana, APA | bab 1-3, pernyataan kesediaan mitra |
| `prototipe-laporan` | prototipe, laporan, diploma, IEEE | bab 1-5, pembimbing tunggal, sertifikat dan media |
| `prototipe-proposal` | prototipe, proposal, diploma, IEEE | bab 1-3 |
| `publikasi-laporan` | publikasi ilmiah, laporan, sarjana, APA | naskah artikel + LoA, homepage jurnal, korespondensi |
| `publikasi-proposal` | publikasi ilmiah, proposal, sarjana, APA | bab 1-3 gaya artikel ilmiah |
| `publikasi-repositori` | publikasi ilmiah, repositori, sarjana, APA | tautan dan keterangan penerbitan saja (panduan hal. 59) |
| `prestasi-laporan` | penyetaraan prestasi, laporan, sarjana, APA | bab 1-4 + sertifikat, pemberitaan media |
| `prestasi-proposal` | penyetaraan prestasi, proposal, sarjana, APA | berkas proposal penyetaraan; panduan hal. 8 menyatakan penyetaraan tidak memerlukan proposal |

Catatan pemakaian:

- Isi bab di dalam contoh ini ditulis lengkap menurut sistematika panduan, bukan kerangka
  kosong. Kalau ingin kerangka beserta catatan pengarah panduan di bawah setiap subbab, pakai
  `\sistematika` (lihat `../uji/sistematika/`) sebagai ganti bab yang ditulis manual.
- Gelar pada contoh jenjang diploma (`prototipe-*`) diisi `Ahli Madya`; panduan tidak menyebut
  gelar jenjang ini, jadi sesuaikan dengan ketentuan prodi Anda.
- Gaya sitasi pada contoh skripsi/proyek/prototipe/prestasi memakai gaya dari opsi kelas
  `sitasi=`. Untuk publikasi ilmiah, panduan hal. 92 butir 6 menetapkan gaya mengikuti jurnal
  tujuan; ganti dengan `sitasibst=<berkas gaya jurnal>`.
- Berkas pustaka contoh ada di `../referensi/contoh.bib` (isi awalnya diambil dari Daftar
  Pustaka panduan hal. 95).
- Logo pada contoh memakai `../logo/logo-unnes.png`: logo UNNES hitam putih berlatarkan transparan
  (lambang + "UNNES" + "UNIVERSITAS NEGERI SEMARANG"). Versi berwarna tersedia dengan
  `logo=logo-unnes-warna`; baris tambahan "Universitas Negeri Semarang" bisa dinyalakan dengan
  `namalogo=true`. Lihat `../logo/README.md`.
- Berkas contoh dihasilkan oleh `../skrip/buat-contoh.py`. Menyunting `main.tex`, isi `bab/`,
  `lampiran/`, dan `gambar/` boleh saja, tetapi menjalankan ulang generator akan menimpanya;
  salin dulu direktorinya bila ingin menyunting bebas.

## Menyalin contoh menjadi dokumen Anda

```bash
cd ..    # akar repo
python3 skrip/salin-dokumen.py contoh/skripsi-laporan ~/tugas-akhir-saya
cd ~/tugas-akhir-saya
./kompilasi.sh        # atau buka direktorinya di code-server/VS Code, lalu Ctrl+S
```

`skrip/salin-dokumen.py` menyalin dokumen tanpa berkas bantu kompilasi sekaligus membereskan
rujukan yang tidak lagi terjangkau dari lokasi baru:

| Rujukan di contoh | Di dokumen salinan | Berkas yang disiapkan |
|---|---|---|
| `\input{../identitas}` | `\input{identitas}` | `identitas.tex` disalin ke direktori dokumen, sunting bebas |
| `\daftarpustaka{../../referensi/contoh}` | `\daftarpustaka{pustaka}` | `pustaka.bib` disalin, tambahkan entri Anda di situ |
| `logodir=../../logo` | `logodir=logo` | logo template dicari lewat TEXINPUTS ke `logo/` repo |

Salinan tetap memakai kelas dan paket dari akar repo, jadi perbaikan pada
`unnes-ta.cls`/`unnes-ta-*.sty` otomatis ikut terpakai. Selama dokumen salinan masih berada di dalam
repo (mis. `proyek_satu/skripsi-laporan`), jalur di `.vscode/settings.json` maupun `kompilasi.sh`
tetap relatif terhadap direktori dokumen sehingga repo boleh dipindah ke PC lain. Hanya salinan di
luar repo yang terpaksa memakai jalur absolut akar repo, dan itu perlu dijalankan ulang
(`python3 skrip/siapkan-vscode.py <direktori dokumen>`) setelah repo template dipindah.

Menyalin dengan `cp -r` biasa juga sah bila dokumen tetap berada di dalam repo — mis.
`cp -r contoh/skripsi-laporan proyek_satu/skripsi-laporan`, karena `../identitas`,
`../../referensi/contoh`, dan `../../logo` masih terjangkau; folder proyek baru itu langsung terurus
(`python3 skrip/siapkan-vscode.py` dan `./skrip/build.sh proyek_satu`). Untuk dokumen yang diletakkan di luar repo, pakai
`skrip/salin-dokumen.py`; `cp -r` ke luar repo membuat ketiga rujukan itu menunjuk ke tempat yang
salah sehingga kompilasi berhenti dengan galat.
