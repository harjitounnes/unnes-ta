# Template Tugas Akhir UNNES (LaTeX)

Template LaTeX modular untuk Tugas Akhir Universitas Negeri Semarang menurut *Panduan Tugas
Akhir Sarjana dan Diploma UNNES 2024*. Kelas `unnes-ta.cls` hanya mengurus opsi dan pemuatan
paket; setiap kelompok aturan format ada di paket `unnes-ta-*.sty` terpisah dan diawali komentar
yang menyebut aturan panduan beserta halaman sumbernya.

Lima jenis TA didukung (skripsi, laporan proyek, prototipe, publikasi ilmiah, penyetaraan
prestasi) dalam mode proposal, laporan, dan repositori, masing-masing punya contoh dokumen utuh
di `contoh/`.

## Mulai cepat

```bash
cd ~/latex/unnes-ta
python3 skrip/salin-dokumen.py contoh/skripsi-laporan ~/tugas-akhir-saya   # salah satu varian
cd ~/tugas-akhir-saya
$EDITOR main.tex         # judul dan data dokumen, urutan bab dan lampiran
$EDITOR bab/*.tex        # isi tiap bab
./kompilasi.sh           # atau cukup Ctrl+S bila disunting lewat code-server/VS Code
```

`skrip/salin-dokumen.py` menyalin dokumen contoh menjadi dokumen mandiri: rujukan berjalur relatif
yang tidak lagi terjangkau dari direktori baru (`\input{../identitas}`,
`\daftarpustaka{../../referensi/contoh}`, `logodir=../../logo`) diganti menjadi rujukan lokal,
`identitas.tex` dan `pustaka.bib` disalin ke direktori dokumen, lalu `.vscode/settings.json` dan
`kompilasi.sh` ikut dibuat. Salinan tetap memakai kelas dan paket template lewat TEXINPUTS ke akar
repo, jadi perbaikan kelas otomatis terpakai. Ingin dokumen tetap di dalam repo? Beri tujuan tanpa
jalur lain, mis. `python3 skrip/salin-dokumen.py contoh/skripsi-laporan tugas-akhir-saya`.

Susunan satu dokumen: `main.tex` (kelas, data identitas dokumen, halaman bagian awal, urutan
`\input`), `bab/NN-*.tex`, `lampiran/NN-*.tex`, dan `gambar/`. Seluruh contoh memakai **satu**
berkas data identitas, yaitu `contoh/identitas.tex`; setiap `main.tex` mengambilnya dengan
`\input{../identitas}` lalu menimpa kunci yang khusus dokumen itu (judul, gelar, pembimbing kedua).

### Menyunting di code-server/VS Code: menyimpan berarti PDF terbaru

Kelas `unnes-ta.cls`, paket `unnes-ta-*.sty`, berkas gaya `bst/`, pustaka `referensi/`, dan `logo/`
ada di akar repo — bukan di dalam direktori dokumen. Supaya hal itu tidak berakhir dengan galat
`File `unnes-ta.cls' not found` saat `main.tex` disunting dari dalam subfolder,
`skrip/siapkan-vscode.py` menuliskan `.vscode/settings.json` di setiap folder dokumen: variabel
TEXINPUTS/BSTINPUTS/BIBINPUTS menunjuk ke akar repo dan resepnya pdflatex → bibtex → pdflatex →
pdflatex dengan `latex-workshop.latex.autoBuild.run = onSave`. Menekan Ctrl+S langsung
memperbarui `main.pdf` tanpa menyetel variabel lingkungan sendiri.

Setelan itu **tanpa jalur PC tertentu**, jadi repo boleh dipindah ke PC lain (nama pengguna, letak
home, dan nama direktori repo boleh berbeda) dan Ctrl+S tetap bekerja: jalur dibangun dari
placeholder `%DIR%` milik LaTeX Workshop — diisi direktori berkas utama saat resep berjalan,
berlaku untuk argumen maupun `env` — dan dari `$TEXMFDIST` yang dikembangkan kpathsea dari
`texmf.cnf` mesin yang dipakai, sehingga letak TeX Live tidak perlu diketahui lebih dahulu.
Skrip bibtex-nya dipanggil lewat `bash` dengan jalur `%DIR%/../..`, bukan sebagai program yang
dieksekusi langsung, karena proses dijalankan tanpa shell sehingga `~` tidak dikembangkan dan bita
executable skrip bisa hilang saat repo dipindah.

```bash
python3 skrip/siapkan-vscode.py                        # akar repo + tiap folder dokumen proyek dan uji/
python3 skrip/siapkan-vscode.py contoh/skripsi-laporan <folder lain>   # hanya folder yang disebut
python3 skrip/siapkan-vscode.py --akar=/path/ke/unnes-ta <folder>      # akar repo yang berbeda
```

Folder proyek dikenali dari isinya, bukan dari namanya: `contoh/`, `harjito/`, dan proyek baru
seperti `proyek_satu/` ikut terurus tanpa menyunting skrip. Urutan pencarian selalu dimulai dari
direktori dokumen (`.`), lalu direktori induk terdekat, sehingga `identitas.tex`, `pustaka.bib`,
atau kelas lokal di folder dokumen menang atas berkas template. Skrip ini hanya perlu dijalankan
ulang bila folder dokumen berada di luar repo (mis. hasil `skrip/salin-dokumen.py` ke
`~/tugas-akhir-saya`) — di situ `%DIR%` tidak bisa menjangkau akar repo dan jalur absolut
terpaksa ditulis.

### Kompilasi dari terminal

```bash
./skrip/build.sh                        # 11 contoh di contoh/ (pdflatex)
./skrip/build.sh proyek_satu            # semua dokumen di proyek_satu/, bukan contoh/
./skrip/build.sh harjito proyek_satu    # dua folder proyek sekaligus
./skrip/build.sh harjito/skripsi-laporan   # satu dokumen saja
./skrip/build.sh proyek_satu --only=skripsi-laporan
python3 uji/cek-vscode.py <folder>      # menirukan resep LaTeX Workshop di folder dokumen
cd <folder-dokumen> && ./kompilasi.sh   # satu dokumen (hasil skrip/salin-dokumen.py)
```

Parameter `build.sh` adalah folder proyek — subfolder akar repo yang memuat direktori dokumen
(`contoh/`, `harjito/`, `proyek_satu/`, ...) — atau langsung satu direktori dokumen yang berisi
`main.tex`; tanpa parameter dipakai `contoh/`. Direktori bantu dikosongkan dengan
`./skrip/build.sh proyek_satu --bersih`.

Dua kali `pdflatex` diperlukan karena Daftar Isi dan label butuh dua pass; `bibtex` hanya perlu
bila dokumen menyitasi pustaka (`\daftarpustaka`) — `skrip/bibtex-bila-perlu.sh` yang dipanggil
resep editor melewatinya sendiri bila berkas `.aux` tidak memuat `\bibdata`. Kompilasi terminal
memakai TEXINPUTS/BSTINPUTS/BIBINPUTS yang sama dengan setelan editor (definisi tunggalnya di
`skrip/siapkan-vscode.py`), jadi hasil keduanya identik.

## Struktur repositori

| Berkas / direktori | Isi |
|---|---|
| `unnes-ta.cls` | Kelas: opsi, validasi nilai opsi, urutan pemuatan paket, metadata PDF |
| `unnes-ta-core.sty` | Ukuran kertas A4, margin 4/3/3/3 cm, huruf Times 12 pt, spasi, nomor halaman |
| `unnes-ta-identitas.sty` | Perintah `\identitas{}` dan 30 kunci data (judul, nama, prodi, pembimbing, penguji, biodata penulis) |
| `unnes-ta-bab.sty` | Judul bab "BAB 1." + nama bab kapital, subbab 1.1, nama bagian berbahasa Indonesia |
| `unnes-ta-tabel-gambar.sty` | Keterangan tabel di atas dan gambar di bawah, penomoran Bab.n, `\sumber{}`, `tabelpanjang` |
| `unnes-ta-sampul.sty` | Sampul, halaman judul, punggung |
| `unnes-ta-pengesahan.sty` | Persetujuan pembimbing, pengesahan tim penguji, pernyataan keaslian |
| `unnes-ta-awal.sty` | Moto dan persembahan, abstrak, abstract, prakata, daftar isi/gambar/tabel/istilah/lampiran |
| `unnes-ta-lampiran.sty` | Lampiran bebas, 15 lampiran wajib siap panggil, biodata penulis |
| `unnes-ta-sistematika.sty` | Kerangka bab/subbab kelima jenis TA beserta catatan pengarah panduan |
| `unnes-ta-sitasi.sty` | Enam preset gaya sitasi (APA bawaan), `\daftarpustaka{}`, `\citemla` |
| `bst/unnes-apalike-apa.bst` | Gaya BibTeX APA milik template (apalike yang disesuaikan: `&` dan DOI) |
| `logo/` | Logo UNNES hitam putih (latar transparan) + versi berwarna + kotak penanda cadangan; `logo/README.md` |
| `referensi/contoh.bib` | Berkas pustaka contoh, isi awalnya dari contoh Daftar Pustaka panduan |
| `contoh/` | Sebelas dokumen TA utuh, satu per varian: tiap direktori berisi `main.tex`, `bab/`, `lampiran/`, `gambar/` (`contoh/README.md` berisi tabelnya) |
| `harjito/`, `proyek_satu/`, … | Folder proyek lain: susunannya sama dengan `contoh/` (satu `identitas.tex` + direktori dokumen). Dikenali otomatis oleh `skrip/build.sh` dan `skrip/siapkan-vscode.py` |
| `contoh/identitas.tex` | Satu-satunya berkas data identitas untuk seluruh contoh: setiap `main.tex` mengambilnya dengan `\input{../identitas}` lalu menimpa kunci khusus dokumennya |
| `uji/` | Dokumen uji, generator, dan pemeriksa otomatis (`cek-contoh.py`, `cek-sistematika.py`, `cek-sitasi.py`, `cek-vscode.py`) |
| `skrip/` | `build.sh`, `qa.py`, `render.py`, `buat-contoh.py`, `verifikasi.py`, `siapkan-logo.py`, `siapkan-vscode.py`, `salin-dokumen.py`, `bibtex-bila-perlu.sh` |
| `.vscode/settings.json` | Setelan LaTeX Workshop untuk akar repo dan tiap folder dokumen: TEXINPUTS/BSTINPUTS/BIBINPUTS ke akar repo plus resep pdflatex → bibtex → pdflatex → pdflatex yang berjalan saat berkas disimpan; dibuat oleh `skrip/siapkan-vscode.py` |
| (luar repo) | `../biodata-narasumber/` — formulir biodata narasumber, proyek terpisah dari template TA |
| `PEMETAAN-PANDUAN.md` | Tabel: setiap aturan panduan (dengan halaman) → perintah/opsi yang menerapkannya |

## Opsi kelas

Ditulis di argumen `\documentclass[...]{unnes-ta}`.

| Opsi | Nilai | Bawaan | Keterangan |
|---|---|---|---|
| `jenis` | `skripsi`, `proyek`, `prototipe`, `publikasi`, `prestasi` | `skripsi` | Menentukan label jenis TA di sampul, sistematika yang dipakai, dan isian lampiran wajib |
| `mode` | `proposal`, `laporan`, `repositori` | `laporan` | `repositori` hanya bermakna untuk `jenis=publikasi` (panduan hal. 59); nilai lain diberi peringatan |
| `jenjang` | `sarjana`, `diploma` | `sarjana` | Menentukan pola pengesahan: 5 baris (sarjana) atau 4 baris (diploma) |
| `sitasi` | `apa`, `ieee`, `mla`, `chicago`, `harvard`, `acs` | `apa` | Preset gaya sitasi (panduan hal. 91-92 menyerahkan pilihan ke fakultas/prodi) |
| `sitasibst` | nama berkas tanpa `.bst` | kosong | Memakai berkas gaya resmi prodi/jurnal, mengalahkan preset |
| `bahasa` | `id`, `en` | `id` | Nama bab, daftar, dan kata "Tabel"/"Gambar" |
| `halaman` | `bawah`, `atas` | `bawah` | Letak nomor halaman (panduan tidak mengatur; lihat Keputusan default) |
| `ukuranlogo` | ukuran TeX | `3cm` | Sisi kotak logo (logo wajib 1:1), hanya di sampul |
| `logodir` | jalur direktori | `logo` | Direktori berkas logo, relatif terhadap berkas utama |
| `logo` | nama berkas tanpa ekstensi | `logo-unnes` | Nama berkas logo (dicari berurutan `.pdf`, `.png`, `.jpg`); `logo-unnes-warna` = versi berwarna |
| `namalogo` | boolean | `false` | Mencetak baris "Universitas Negeri Semarang" di bawah logo sampul (bawaan mati karena logo bawaan sudah memuatnya) |
| `spasi` | angka | otomatis | Menimpa spasi menurut mode (bawaan: 1,5 laporan; 1,15 proposal; 1,0 abstrak) |
| `duasisi` | boolean | `false` | Mencetak bolak-balik (margin 4 cm di kiri semua halaman isi) |
| `draft` | boolean | `false` | Meneruskan opsi draft ke kelas `report`: kotak penanda overfull terlihat, gambar cepat |
| `catatan` | boolean | `true` | Mencetak catatan pengarah panduan di kerangka `\sistematika` |
| `opsional` | boolean | `false` | Menyertakan seluruh subbab opsional ("bila ada") pada kerangka `\sistematika` |

Nilai opsi yang salah langsung ditolak, mis. `jenis=skripsi2` menghasilkan
`Class unnes-ta Error: Nilai opsi jenis tidak dikenal` beserta daftar nilai yang tersedia.
Boolean juga bisa diubah di preamble: `\unnescatatanfalse`, `\unnesopsionaltrue`.

## Isi dokumen

### Data identitas

Seluruh contoh memakai **satu** berkas data identitas: `contoh/identitas.tex` (nama, NIM, prodi,
fakultas, pembimbing, tim penguji, biodata). Setiap `main.tex` mengambil berkas itu dengan
`\input{../identitas}`, lalu hanya menambah atau menimpa kunci yang khusus dokumen tersebut:

```latex
\input{../identitas}                              % satu sumber data untuk semua contoh
\identitas{
  judul = {Pengembangan Media Pembelajaran ...},  % hanya ada di dokumen ini
  gelar = {Sarjana Pendidikan},
}
```

Bila template dipakai pada dokumen Anda sendiri, cukup satu panggilan `\identitas{...}` berisi
seluruh kunci berikut:

```latex
\identitas{
  judul       = {Judul Tugas Akhir dalam Huruf Kapital},
  nama        = {Nama Mahasiswa},   nim = {1234567890},
  prodi       = {Pendidikan Teknik Informatika}, fakultas = {Fakultas Teknik},
  gelar       = {Sarjana Pendidikan}, kota = {Semarang}, tahun = {2026},
  pembimbinga = {Dr. Pembimbing Satu, M.Kom.}, pembimbinganip = {198001012005011001},
  pembimbingb = {Dr. Pembimbing Dua, M.Pd.},   pembimbingbnip = {1985020220012002},
  ketua       = {Prof. Dr. Ketua Penguji, M.Pd.}, ketuanip = {196001011990031001},
  sekretaris  = {Dr. Sekretaris Penguji, M.Kom.}, sekretarisnip = {197002022000031002},
  penguji1    = {Dr. Penguji Satu, M.Pd.}, penguji1nip = {...},
  penguji2    = {Dr. Penguji Dua, M.Kom.}, penguji2nip = {...},
  penguji3    = {Dr. Pembimbing Satu, M.Kom.}, penguji3nip = {...},   % pola sarjana
  hari = {Senin}, tanggal = {12 Januari}, tanggalpersetujuan = {10 Januari 2026},
  tanggalpernyataan = {10 Januari 2026},
  tempatlahir = {Semarang}, tanggallahir = {1 Januari 2004},
  alamat = {Jl. ...}, surel = {nama@students.unnes.ac.id}
}
```

Kunci yang tidak diisi dibiarkan kosong dan barisnya hilang sendiri (mis. `pembimbingb` pada
jenjang diploma yang hanya punya satu pembimbing, atau `penguji3` pada pola diploma).
`tanggalpersetujuan`/`tanggalpernyataan` boleh berisi tahun saja; nama kota sudah dicetak
halaman sehingga tidak perlu diulang.

### Halaman bagian awal

```latex
\bagianawal
\sampul            \halamanjudul       \punggung        % punggung: judul saja, satu halaman
\persetujuanpembimbing   \pengeshantimpenguji   \pernyataankeaslian
\motopersembahan{\begin{center}``Moto...''\end{center} Persembahan: ...}
\abstrak[kata kunci, dipisah koma]{...}   \abstracten[translated keywords]{...}
\begin{prakata} ... \end{prakata}
\tandatanganprakata{penulis}          % blok tanda tangan prakata, bisa disesuaikan
\daftarisi \daftargambar \daftartabel
\daftaristilah{\istilah{istilah}{penjelasan} \istilah{istilah lain}{penjelasan}}
\daftarlampiran
\bagianutama
```

Proposal memakai bagian awal yang lebih pendek: sampul, halaman judul, persetujuan pembimbing,
daftar isi, daftar tabel/gambar/istilah, daftar lampiran. Halaman pengesahan, pernyataan, moto,
abstrak, dan prakata hanya ada pada laporan. Kecuali halaman judul yang mengulang sampul, setiap
perintah di atas menghasilkan satu halaman dan menambah entri daftar isinya sendiri.

### Bab, tabel, gambar, persamaan

```latex
\chapter{PENDAHULUAN}      \section{Latar Belakang}      \subsection{...}
\begin{table}[htbp]\centering
  \caption{Ringkasan penelitian terdahulu}   \label{tab:terdahulu}
  \begin{tabular}{cll} ... \end{tabular}
  \sumber{penulis dari berbagai sumber (2026)}
\end{table}
\begin{figure}[htbp]\centering
  \includegraphics[width=8cm]{gambar-alur}
  \caption{Alur penelitian}   \label{gam:alur}   \sumber{Dokumentasi penulis (2026)}
\end{figure}
```

Keterangan tabel dicetak di atas tabel, keterangan gambar di bawah gambar (panduan hal. 91 hanya
mewajibkan urut sesuai pembahasan; letak keterangan adalah keputusan default template).
Penomoran otomatis `Tabel 2.1`, `Gambar 2.1`, `(2.1)` mengikuti nomor bab. Untuk tabel yang
melampaui satu halaman gunakan lingkungan `tabelpanjang`. `\unnesjudulhalaman{...}` membuat
halaman khusus berjudul terpusat (mis. daftar singkatan atau halaman pernyataan tambahan);
`\tambahkandaftarisi{...}` menambahkan entri manual ke Daftar Isi.

### Sistematika kerangka per jenis TA

```latex
\sistematika                % otomatis memilih menurut opsi jenis dan mode
\sistematikaskripsi \sistematikaproyek \sistematikaprototipe \sistematikapublikasi \sistematikaprestasi
```

Kerangka ini mencetak bab dan subbab menurut panduan, dan di bawah setiap subbab ada catatan
miring berisi aturan panduan (mis. "Panduan hal. 14-15: latar belakang memuat kondisi nyata,
kesenjangan, penelitian terdahulu, dan kebaruan"). Catatan dimatikan dengan `catatan=false`;
subbab "bila ada" dimunculkan dengan `opsional=true` atau `\unnesopsionaltrue`.

### Sitasi dan daftar pustaka

```latex
\citep{creswell2018research}      \citet{patten2017understanding}      % gaya nama-tahun
\citemla[23]{patten2017understanding}     % bentuk MLA (Nama 23); galat pada gaya bernomor
\daftarpustaka{../../referensi/contoh}    % argumen wajib: berkas .bib tanpa ekstensi
```

Mengganti gaya cukup dengan opsi kelas, dan bila prodi atau jurnal menetapkan berkas gayanya
sendiri pakai `sitasibst=nama-berkas` (berkas `.bst` diletakkan di `bst/` atau di direktori
dokumen). Lihat bagian Kesetaraan gaya sitasi di bawah.

### Lampiran dan biodata

```latex
\bagianakhir
\daftarpustaka{referensi/contoh}
\lampiran{Lampiran Instrumen Penelitian}{...isi...}
\lampiranplaceholder{Lampiran Surat Izin Penelitian}{sisipkan salinan surat di sini}
\lampiranskpembimbing \lampiranskpenguji \lampiraninstrumen \lampiranmitra \lampiransketsa
\lampiranluaranhki \lampiranmedia \lampiranhomepagejurnal \lampiranloa \lampirankorespondensi
\lampiranpernyataankomitmen \lampiranizinetik \lampiranbuktiizinpenelitian
\lampiransertifikatprestasi \lampiranpemberitaanmedia \lampirandokumentasi
\biodatapenulis{...}
```

Setiap lampiran masuk otomatis ke Daftar Lampiran dengan penomoran "LAMPIRAN 1", "LAMPIRAN 2", …
Perintah `\lampiranplaceholder` mencetak halaman dengan keterangan singkat sebagai tempat
menyisipkan salinan dokumen resmi (SK, surat izin, sertifikat, bukti korespondensi).

## Kesetaraan gaya sitasi

| Preset | Berkas gaya | Bentuk sitasi | Batas kesetiaan |
|---|---|---|---|
| `apa` (bawaan) | `unnes-apalike-apa.bst` milik template | (Martin, 2014), (Febriani & Sugiarto, 2020; Shils, 1993) | Sesuai APA 7 untuk `&`, tahun, urutan, DOI. Belum: edisi ditulis "5 edition", lokasi penerbit masih dicetak, nomor volume tidak miring |
| `ieee` | `ieeetr.bst` | [1], [4, 5] | Bukan `IEEEtran.bst` resmi |
| `mla` | `plainnat.bst` | (Martin 2014), bantuan `\citemla[hal]` | Berkas gaya MLA resmi tidak ada di TeX Live ini |
| `chicago` | `apalike.bst` | (Martin 2014) | Chicago author-date, bukan Chicago penuh |
| `harvard` | `apalike.bst` | (Martin 2014) | Gaya Harvard bervariasi antarinstitusi |
| `acs` | `unsrt.bst` | angka superskrip | Berkas gaya ACS resmi tidak ada di TeX Live ini |

Bila berkas gaya preset tidak ditemukan, kelas memakai `apalike.bst` dan mencetak peringatan
beserta cara memperbaikinya. Untuk memakai berkas resmi prodi/jurnal:
`\documentclass[...,sitasibst=unnes-ta-jurnal]{unnes-ta}` (berkas `bst/unnes-ta-jurnal.bst`),
dan tandai ketidaksesuaian gaya di laporan bila ada.

## Keputusan default (hal yang panduan tidak atur)

| Hal | Nilai yang dipakai | Alasan |
|---|---|---|
| Letak nomor halaman | bawah-tengah; romawi kecil pada bagian awal, angka arab pada bagian utama | Panduan hanya menyebut "halaman berjalan"; letak bawah-tengah lazim di UNNES. Ganti dengan `halaman=atas` |
| Format judul bab | dua baris terpusat: "BAB 1." lalu "PENDAHULUAN" | Panduan menunjukkan contoh tanpa mengatur tata letak |
| Letak keterangan tabel/gambar | tabel di atas, gambar di bawah, rata kiri, diikuti baris `Sumber:` | Hanya urutan penampilan yang diatur (panduan hal. 91) |
| Spasi daftar pustaka | dalam entri tunggal, antarentri 6 pt, indentasi menggantung 1 cm | Diukur dari contoh panduan hal. 95 |
| Sampul | teks hitam putih di atas kertas putih, logo 3 cm (1:1) di tengah atas | Panduan menampilkan contoh tanpa warna; untuk laporan publikasi ilmiah dan penyetaraan prestasi panduan meminta *hard cover* berwarna sesuai fakultas (hal. 59, 73) — warna bahan jilid dipilih saat penjilidan dan tidak dapat diwakili berkas PDF |
| Penomoran lampiran | "LAMPIRAN 1", walaupun panduan menyebut "Lampiran ..." di daftar | Seragam dan mudah dirujuk |
| Font saat Times New Roman tidak terpasang | `mathptmx` (Nimbus/Times, pdflatex) atau TeX Gyre Termes (lualatex) | Metriknya sama dengan Times New Roman |
| Nomor halaman sampul | sampul, halaman judul, punggung tanpa nomor; penghitung halaman mulai di halaman persetujuan | Kebiasaan naskah TA UNNES |

## Kendala TeX Live di mesin ini (tanpa sudo)

Paket berikut tidak terpasang: `tocloft`, `titlesec`, `biblatex`/`biber`, `csquotes`, `newtx`,
`mini toc`, `latexmk`, `xelatex`, `luaotfload.sty`, dan `indonesian.ldf`. Konsekuensinya: Daftar
Isi dan judul bab dikerjakan manual di kelas, nama bagian berbahasa Indonesia memakai
`\addto\captionsenglish{...}`, sitasi memakai `natbib` + `bibtex`, dan `lualatex` otomatis jatuh
ke `mathptmx` (Type1) karena fontspec butuh `luaotfload`. Tambahan paket dapat dipasang tanpa sudo
lewat `tlmgr --usermode install <paket>` ke `~/texmf`; setelah itu `lualatex` akan memakai Times
New Roman atau TeX Gyre Termes lewat fontspec.

## Verifikasi

```bash
./skrip/build.sh                    # kompilasi 11 contoh (pdflatex)
./skrip/build.sh proyek_satu        # kompilasi proyek lain, bukan contoh/
./skrip/build.sh --only=skripsi-laporan
./skrip/build.sh --engine=lualatex
./skrip/build.sh --draft            # satu pass tanpa PDF: memeriksa galat dengan cepat
./skrip/build.sh --bersih           # hapus berkas bantu
python3 skrip/qa.py                 # ukur PDF: A4, margin, huruf, spasi, nomor halaman, penomoran
python3 skrip/qa.py --uji           # ikut memeriksa dokumen uji
python3 skrip/render.py contoh/skripsi-laporan --hal=1-8   # PNG di hasil/ untuk diperiksa mata
python3 uji/cek-contoh.py           # urutan bagian, jumlah bab, lampiran, bibliografi
python3 uji/cek-sistematika.py      # 12 varian kerangka sesuai panduan (dijalankan di uji/sistematika)
python3 uji/cek-sitasi.py           # bentuk sitasi dan ukuran daftar pustaka (dijalankan di uji/sitasi)
python3 uji/cek-vscode.py           # tirukan resep LaTeX Workshop: semua folder ber-.vscode
python3 uji/cek-vscode.py contoh/skripsi-laporan <folder-dokumen>   # folder tertentu saja
python3 uji/cek-vscode.py --workspace=akar   # folder yang dibuka di editor = akar repo
```

`uji/cek-vscode.py` tidak hanya menjalankan resepnya: setelan yang masih memuat jalur milik PC
tempat skrip dijalankan (`/home/...`, `~/...`) ditolak untuk folder di dalam repo, supaya setelan
yang tampak jalan di mesin ini tidak diam-diam rusak setelah repo dipindah.

`skrip/qa.py` mengukur dari PDF, bukan dari berkas sumber: ukuran halaman, margin 4/3/3/3 cm pada
seluruh halaman isi, keluarga dan ukuran huruf, spasi antarbaris menurut mode, nomor halaman
romawi/arab, dan penomoran tabel/gambar harus mengikuti nomor bab. Hasil terakhir: 11/11 contoh
lolos, dokumen uji 36/37 (satu-satunya temuan adalah dokumen uji negatif yang memang harus gagal).

## Mengganti logo dan berkas gaya

1. Sampul bawaan memakai `logo/logo-unnes.png` — logo UNNES **hitam putih** (lambang + tulisan
   "UNNES" + "UNIVERSITAS NEGERI SEMARANG", latar transparan). Berkas itu dibuat dari logo berwarna
   di akar repo (`Logo-Transparan-Warna-1.png`) oleh `skrip/siapkan-logo.py`; versi berwarnanya
   tersimpan sebagai `logo/logo-unnes-warna.png` dan dipakai dengan `logo=logo-unnes-warna`.
   Nama berkas dan besar logo diatur opsi `logo=`/`logodir=`/`ukuranlogo=`; baris tambahan
   "Universitas Negeri Semarang" di bawah logo bisa dinyalakan dengan `namalogo=true`.
   Selengkapnya di `logo/README.md`.
2. Berkas gaya BibTeX resmi prodi diletakkan di `bst/` dan dipanggil dengan `sitasibst=`.
3. Template ini tidak menyertakan teks panduan; rujukan halaman pada komentar dan dokumentasi
   mengacu pada *Panduan Tugas Akhir Sarjana dan Diploma UNNES 2024*.
