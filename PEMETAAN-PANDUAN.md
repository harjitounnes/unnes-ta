# Pemetaan aturan Panduan TA UNNES 2024 ke kode template

Setiap baris memetakan satu aturan panduan (dengan nomor halaman) ke perintah atau opsi di
template, berkas pelaksananya, dan cara aturan itu diverifikasi. Nomor halaman mengacu pada
*Panduan Tugas Akhir Sarjana dan Diploma UNNES 2024* (berkas PDF di `~/latex/`).

Keterangan kolom verifikasi: **ukur** = angka diukur dari PDF hasil kompilasi dengan
`skrip/qa.py`/`mutool`; **lihat** = diperiksa mata pada PNG hasil `skrip/render.py`;
**log** = peringatan/galat yang dicetak saat kompilasi; **cek** = pemeriksa otomatis
(`uji/cek-contoh.py`, `uji/cek-sistematika.py`, `uji/cek-sitasi.py`).

## 1. Format penulisan (proposal hal. 13/29/43, laporan hal. 16/31/45)

| Aturan menurut panduan | Perintah/opsi | Berkas | Verifikasi |
|---|---|---|---|
| "Tipe huruf menggunakan Times New Roman ukuran 12" (hal. 13, 16, 29, 31, 43, 45) | `mathptmx` (pdflatex) atau `fontspec` + Times New Roman/TeX Gyre Termes (lualatex), semuanya pada 12 pt | `unnes-ta-core.sty` | ukur: huruf `NimbusRomNo9L` 11,96 pt pada 11 contoh |
| "Teks menggunakan jarak baris 1,5 spasi dan perataan teks rata kiri-kanan" (hal. 16) | `\setstretch{1.5}` otomatis saat `mode=laporan`; `\unnesspasiabstrak` untuk abstrak | `unnes-ta-core.sty` | ukur: 21,70 pt pada semua contoh mode laporan |
| "jarak baris 1,15 spasi" untuk proposal (hal. 13, 29, 43) | `\setstretch{1.15}` otomatis saat `mode=proposal` | `unnes-ta-core.sty` | ukur: 16,60 pt pada semua contoh mode proposal |
| "Abstrak ditulis dengan spasi 1.0 (single space)" (hal. 16) | `\setstretch{1.0}` khusus halaman abstrak/abstract | `unnes-ta-awal.sty` | ukur: 14,40 pt pada halaman abstrak |
| "Tata letak halaman menggunakan ukuran kertas A4, satu kolom, dengan margin: kiri 4 cm, kanan 3 cm, atas 3 cm, bawah 3 cm" (hal. 13, 16, 29, 31, 43, 45) | `geometry` dengan `a4paper` dan margin tersebut; satu kolom; `\microtypesetup{protrusion=false}` agar tepi teks persis di margin | `unnes-ta-core.sty` | ukur: A4 595,28 × 841,89 pt dan selisih margin ≤ 0,2 pt pada 11 contoh |
| Jumlah halaman, ukuran kertas, dan jenis huruf sama untuk semua jenis TA | satu paket `unnes-ta-core` dipakai semua jenis | `unnes-ta-core.sty` | ukur pada 11 contoh dari 5 jenis |

## 2. Bagian awal laporan dan proposal

Bagian awal diurutkan menurut panduan: laporan skripsi hal. 16-18, proposal skripsi hal. 14-15,
laporan proyek hal. 31-32, proposal proyek hal. 29-31, laporan prototipe hal. 45-46, proposal
prototipe hal. 43-45, laporan publikasi ilmiah hal. 58-59, proposal publikasi hal. 57-58,
laporan penyetaraan prestasi hal. 72-74.

| Butir panduan | Perintah | Berkas | Verifikasi |
|---|---|---|---|
| Sampul (soft cover untuk proposal, hard cover untuk laporan) | `\sampul` | `unnes-ta-sampul.sty` | lihat hlm-01; ukur 14 pt judul, 12 pt isi |
| Halaman judul "memiliki format yang sama dengan sampul luar" (hal. 14) | `\halamanjudul` | `unnes-ta-sampul.sty` | cek: halaman 2 = sampul |
| Punggung berisi judul (contoh hal. 23/37/51/66/78) | `\punggung` — judul dibungkus `\rotatebox` + `\parbox` setinggi textheight | `unnes-ta-sampul.sty` | lihat hlm-03 |
| Persetujuan Pembimbing (contoh hal. 24/38/52/67/79) | `\persetujuanpembimbing` | `unnes-ta-pengesahan.sty` | lihat hlm-04 |
| Pengesahan Tim Penguji, 5 baris untuk sarjana (contoh hal. 25) | `\pengeshantimpenguji` (jenjang sarjana) | `unnes-ta-pengesahan.sty` | lihat hlm-05 |
| Pengesahan Tim Penguji, 4 baris untuk diploma (contoh hal. 53) | `\pengeshantimpenguji` (jenjang diploma) | `unnes-ta-pengesahan.sty` | lihat hlm-05 pada contoh prototipe |
| Pernyataan keaslian bermaterai (contoh hal. 26/40/54/69/81) | `\pernyataankeaslian` — kotak materai 10.000 | `unnes-ta-pengesahan.sty` | lihat hlm-06 |
| Moto dan Persembahan (hal. 16, 31) | `\motopersembahan{...}` | `unnes-ta-awal.sty` | cek bagian awal contoh |
| Abstrak memuat judul, nama penulis, jenis TA, prodi/fakultas, pembimbing, kata kunci (hal. 16-17) | `\abstrak[kata kunci]{...}` dan `\abstracten[...]{...}` | `unnes-ta-awal.sty` | lihat; ukur spasi 14,40 pt |
| Prakata (hal. 17) | lingkungan `prakata` + `\tandatanganprakata{...}` | `unnes-ta-awal.sty` | cek bagian awal |
| Daftar Isi, Daftar Tabel, Daftar Gambar, Daftar Istilah, Daftar Lampiran | `\daftarisi`, `\daftartabel`, `\daftargambar`, `\daftaristilah{\istilah{}{}}`, `\daftarlampiran` | `unnes-ta-awal.sty` | cek: entri daftar terisi; lihat hlm-11 |
| Proposal tidak memuat pengesahan, pernyataan, moto, abstrak, dan prakata | perintah-perintah itu hanya dipanggil di bagian awal laporan | `contoh/*/main.tex` | cek: 5 dokumen proposal tidak memuat istilah itu |

## 3. Sistematika isi per jenis TA

| Jenis, mode | Halaman panduan | Perintah | Verifikasi |
|---|---|---|---|
| Skripsi proposal (bab 1-3) | hal. 14-15 | `\sistematikaskripsi` / `\sistematika` | cek-sistematika: 1..3 |
| Skripsi laporan (bab 1-5) | hal. 16-18 | idem | cek-sistematika: 1..5 |
| Proyek proposal (bab 1-3) | hal. 29-31 | `\sistematikaproyek` | cek-sistematika: 1..3 |
| Proyek laporan (bab 1-5) | hal. 31-32 | idem | cek-sistematika: 1..5 |
| Prototipe proposal (bab 1-3) | hal. 43-45 | `\sistematikaprototipe` | cek-sistematika: 1..3 |
| Prototipe laporan (bab 1-5) | hal. 45-46 | idem | cek-sistematika: 1..5 |
| Publikasi ilmiah proposal (bab 1-3) | hal. 57-58 | `\sistematikapublikasi` | cek-sistematika: 1..3 |
| Publikasi ilmiah laporan: bagian utama hanya naskah artikel | hal. 58-59 | idem (`mode=laporan` → satu bab "NASKAH ARTIKEL ILMIAH") | cek-sistematika: 1 |
| Publikasi ilmiah mode repositori: tanpa isi artikel, hanya tautan dan keterangan | hal. 59 | `mode=repositori` → satu bab "TAUTAN DAN KETERANGAN PUBLIKASI" | cek-sistematika: 1 |
| Penyetaraan prestasi laporan (empat bab) | hal. 72-74 | `\sistematikaprestasi` | cek-sistematika: 1..4 |
| Penyetaraan prestasi tidak memerlukan proposal | hal. 8 | peringatan resmi saat `jenis=prestasi,mode=proposal` | log: peringatan tercetak |
| Subbab "bila ada" | hal. 14-18, 29-32, 43-46 | `opsional=true` atau `\unnesopsionaltrue` | cek: 6 subbab bertanda opsional |
| Catatan pengarah panduan di kerangka | — | `catatan=true` (bawaan) | cek: 12 catatan pada 12 varian; `catatan=false` → 0 |

## 4. Penomoran

| Aturan | Perintah/opsi | Berkas | Verifikasi |
|---|---|---|---|
| Judul bab "BAB 1." dengan nama bab | `\chapter{NAMA BAB}` | `unnes-ta-bab.sty` | ukur + lihat: "BAB 1." lalu "PENDAHULUAN" |
| Subbab bernomor 1.1, 1.1.1; Daftar Isi sampai dua level | `\section`, `\subsection`, `tocdepth=2` | `unnes-ta-bab.sty` | lihat hlm-11 |
| "Setiap tabel dan gambar dalam pembahasan harus sesuai dengan urutan penampilan" (hal. 91) | `\caption` + `\label` pada `table`/`figure` | `unnes-ta-tabel-gambar.sty` | cek-contoh + qa: nomor "Tabel n.m"/"Gambar n.m" cocok dengan nomor babnya |
| Sumber tabel/gambar | `\sumber{...}` di bawah tabel/gambar | `unnes-ta-tabel-gambar.sty` | lihat hlm-16 |
| Lampiran dinomori pada Daftar Lampiran | `\lampiran{nama}{isi}` → "LAMPIRAN n" pada `.loa` | `unnes-ta-lampiran.sty` | cek: jumlah lampiran per varian |

## 5. Kutipan dan daftar pustaka

| Aturan | Perintah/opsi | Berkas | Verifikasi |
|---|---|---|---|
| "Fakultas atau prodi dapat menetapkan penggunaan gaya sitasi" dari APA, IEEE, MLA, Chicago, Harvard, ACS (hal. 91-92) | `sitasi=apa|ieee|mla|chicago|harvard|acs` | `unnes-ta-sitasi.sty` | cek-sitasi: 6/6 bentuk sitasi sesuai gaya |
| Berkas gaya resmi prodi/jurnal dipakai bila ada | `sitasibst=nama-berkas` | `unnes-ta-sitasi.sty`, `bst/` | log: `\IfFileExists` melaporkan gaya yang dipakai |
| Daftar Pustaka disusun menurut gaya terpilih (contoh hal. 95) | `\daftarpustaka{berkas-bib}` — judul terpusat, spasi tunggal, indentasi menggantung 1 cm, antarentri 6 pt | `unnes-ta-sitasi.sty`, `bst/unnes-apalike-apa.bst` | ukur dari PDF: menggantung 28,3 pt (1 cm), dalam entri 14,5 pt, antarentri 20,5 pt — sama dengan contoh panduan hal. 95 |
| DOI dicantumkan sebagai tautan pada entri APA | patch `EN TRY` dan `fin.entry` pada berkas `.bst` template | `bst/unnes-apalike-apa.bst` | lihat halaman DAFTAR PUSTAKA; log bebas galat `\url` |

## 6. Lampiran wajib per jenis

| Jenis | Lampiran menurut panduan (halaman) | Perintah siap panggil | Verifikasi |
|---|---|---|---|
| Skripsi | Biodata penulis, SK pembimbing, SK penguji, instrumen (hal. 18) | `\biodatapenulis`, `\lampiranskpembimbing`, `\lampiranskpenguji`, `\lampiraninstrumen` | cek: contoh skripsi punya 5-6 lampiran |
| Proposal skripsi | Biodata penulis, SK pembimbing, instrumen (hal. 15) | idem | cek: proposal punya lampiran tersebut |
| Laporan proyek | Biodata penulis, SK pembimbing, SK penguji, pernyataan kesediaan mitra, dokumentasi, publikasi media massa (hal. 32-33) | `\lampiranmitra`, `\lampirandokumentasi`, `\lampiranmedia` | cek: contoh proyek punya 6-8 lampiran |
| Proposal proyek | Biodata penulis, SK pembimbing, pernyataan kesediaan mitra (hal. 31) | `\lampiranmitra` | cek |
| Laporan prototipe | Biodata penulis, SK pembimbing, draf karya/sketsa/storyboard, luaran HKI, publikasi media, dokumentasi (hal. 46) | `\lampiransketsa`, `\lampiranluaranhki`, `\lampiranmedia`, `\lampirandokumentasi` | cek: contoh prototipe punya 5-6 lampiran |
| Proposal prototipe | Biodata penulis, SK pembimbing, draf karya/sketsa (hal. 45) | `\lampiransketsa` | cek |
| Laporan publikasi ilmiah | Biodata penulis, SK pembimbing, homepage jurnal, letter of acceptance, korespondensi, bukti similarity (hal. 59-60) | `\lampiranhomepagejurnal`, `\lampiranloa`, `\lampirankorespondensi` | cek: contoh publikasi punya 4-5 lampiran |
| Laporan penyetaraan prestasi | Biodata penulis, SK pembimbing, sertifikat prestasi, pemberitaan media, dokumentasi, bukti HKI (hal. 73-74) | `\lampiransertifikatprestasi`, `\lampiranpemberitaanmedia`, `\lampiranpernyataankomitmen` | cek: contoh prestasi punya 4-5 lampiran |
| Izin etik penelitian yang memakai subjek manusia (hal. 6, 8) | `\lampiranizinetik` | `unnes-ta-lampiran.sty` | perintah tersedia; dipakai pada contoh skripsi |
| Prototipe wajib terdaftar HKI DJKI (hal. 5) | `\lampiranluaranhki` | `unnes-ta-lampiran.sty` | perintah tersedia; dipakai pada contoh prototipe |
| Lampiran berbentuk salinan dokumen resmi | `\lampiranplaceholder{nama}{keterangan}` | `unnes-ta-lampiran.sty` | lihat hlm lampiran contoh |

## 7. Hal yang panduan tidak atur (keputusan default template)

| Hal | Nilai yang dipakai | Catatan |
|---|---|---|
| Letak nomor halaman | bawah-tengah; romawi kecil (bagian awal) lalu angka arab (bagian utama) | Panduan hanya menyebut "halaman berjalan"; opsi `halaman=atas` tersedia. Diperiksa `qa.py` |
| Bentuk judul bab | dua baris terpusat: "BAB 1." / "PENDAHULUAN" | Panduan memuat contoh tanpa mengatur tata letaknya |
| Letak keterangan tabel/gambar | tabel di atas, gambar di bawah, rata kiri, diikuti baris sumber | Panduan hanya mengatur urutan (hal. 91) |
| Sampul publikasi ilmiah dan penyetaraan prestasi: "hard cover dengan warna sesuai fakultas" (hal. 59, 73) | Sampul PDF tetap hitam putih; warna hard cover dipilih saat penjilidan | Warna bahan jilid tidak dapat diwakili PDF; dicatat di README |
| Penomoran lampiran | "LAMPIRAN 1", "LAMPIRAN 2", … pada Daftar Lampiran | Panduan menulis "Lampiran ..." pada daftar contohnya |
| Ukuran logo sampul | `ukuranlogo=3cm` sebagai sisi terpanjang, proporsi gambar selalu dijaga | Panduan tidak menyebut besar pastinya; angka 3 cm mengikuti proporsi logo pada contoh sampul panduan |
| Isi logo | Logo lengkap hitam putih: lambang + "UNNES" + "UNIVERSITAS NEGERI SEMARANG", latar transparan (`logo/logo-unnes.png`, dibuat `skrip/siapkan-logo.py` dari logo berwarna di akar repo) | Panduan hal. 22, 35, 49, 64, 77 meminta logo proporsional P:L = 1:1 "tanpa teks UNNES"; letakkan lambang persegi sebagai `logo/logo-unnes.png` bila harus persis mengikuti bunyi panduan |

## 8. Cara memverifikasi ulang pemetaan ini

```bash
cd ~/latex/unnes-ta
./skrip/build.sh && python3 skrip/qa.py           # format: huruf, spasi, margin, nomor halaman
python3 uji/cek-contoh.py                         # bagian awal/akhir, jumlah bab, lampiran, bibliografi
(cd uji/sistematika && python3 ../cek-sistematika.py)   # sistematika 12 varian
(cd uji/sitasi && python3 ../cek-sitasi.py)             # gaya sitasi 6 preset
python3 uji/cek-vscode.py                         # resep LaTeX Workshop + TEXINPUTS di tiap folder dokumen
python3 skrip/render.py contoh/skripsi-laporan --hal=1-8   # pemeriksaan mata
```

Hasil terakhir: build 11/11 tanpa galat; `qa.py` 11/11 lolos; `cek-contoh.py` 11/11;
`cek-sistematika.py` 12/12; `cek-sitasi.py` 6/6; `cek-vscode.py` 22 folder dokumen tanpa galat
(dijalankan tanpa mewarisi TEXINPUTS dari shell, jadi lolosnya berarti setelan
`.vscode/settings.json` sendiri yang mencukupi).

## 9. Susunan berkas dokumen

Satu dokumen contoh = satu direktori: `main.tex` (kepala, data identitas dokumen, halaman bagian
awal, urutan `\input`), `bab/NN-*.tex`, `lampiran/NN-*.tex`, dan `gambar/`. Seluruh contoh memakai
**satu** berkas data identitas, `contoh/identitas.tex`, yang diambil tiap `main.tex` lewat
`\input{../identitas}` sebelum `\identitas{...}` khusus dokumen. Jadi pergantian nama, NIM, prodi,
pembimbing, atau penguji cukup dilakukan sekali untuk semua contoh proposal/laporan/repositori.
Aturan panduan yang bersangkutan tetap dipetakan lewat perintah `\identitas{}` pada bagian 2.

Kelas, paket `unnes-ta-*.sty`, berkas gaya `bst/`, pustaka `referensi/`, dan logo sengaja tetap
tinggal di akar repo (bukan disalin ke tiap direktori dokumen). Supaya berkas-berkas itu terjangkau
saat `main.tex` disunting dari dalam direktori dokumen, tiap direktori memuat
`.vscode/settings.json` berisi TEXINPUTS/BSTINPUTS/BIBINPUTS ke akar repo dengan resep
pdflatex → bibtex → pdflatex → pdflatex yang berjalan saat berkas disimpan
(`skrip/siapkan-vscode.py`, diperiksa `uji/cek-vscode.py`). Jalurnya ditulis lewat placeholder
`%DIR%` dan `$TEXMFDIST`, bukan jalur absolut PC ini, sehingga repo tetap terkompilasi setelah
dipindah ke PC lain. Dokumen yang disalin ke luar repo dibereskan rujukannya oleh
`skrip/salin-dokumen.py`; lihat `contoh/README.md`. Dokumen dari beberapa folder proyek
(`contoh/`, `harjito/`, `proyek_satu/`, ...) dikompilasi serentak dengan
`skrip/build.sh <folder proyek>`.

## Di luar cakupan panduan

Formulir biodata narasumber (kop instansi, baris isian, blok tanda tangan) tidak berasal dari panduan
TA dan tidak lagi berada di repositori ini; proyeknya terpisah di `../biodata-narasumber/`.
