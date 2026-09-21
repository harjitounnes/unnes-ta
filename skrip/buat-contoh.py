#!/usr/bin/env python3
"""Membuat dokumen contoh di direktori contoh/ (todo t61-t613).

Setiap contoh adalah dokumen utuh yang bisa langsung disalin mahasiswa, dengan susunan:
  contoh/identitas.tex             data identitas bersama seluruh contoh (satu sumber)
  contoh/<nama>/main.tex           kelas, data identitas dokumen, urutan bab dan lampiran
  contoh/<nama>/bab/NN-*.tex       isi tiap bab
  contoh/<nama>/lampiran/NN-*.tex  isi tiap lampiran
  contoh/<nama>/gambar/*.pdf       gambar dokumen (berkas sumber .tex ikut disertakan)

Susunannya mengikuti panduan untuk jenis dan mode yang bersangkutan:
  bagian awal  : sampul, halaman judul, punggung, persetujuan, pengesahan, pernyataan,
                 moto, abstrak, abstract, prakata, daftar isi/gambar/tabel/istilah/lampiran
                 (proposal hanya: sampul, halaman judul, persetujuan pembimbing, daftar isi/tabel/gambar/istilah)
  bagian utama : bab dan subbab sesuai sistematika jenis TA (tanpa catatan pengarah,
                 karena contoh sudah berisi tulisan)
  bagian akhir : daftar pustaka, lampiran wajib, biodata penulis

Jalankan:  python3 skrip/buat-contoh.py
"""
import pathlib
import re
import shutil
import subprocess
import sys

# ============================================================== kerangka dokumen
KEPALA = """%% Dokumen contoh: {nama} — {ket}
%% Susunan berkas dokumen ini:
%%   main.tex          kelas, data identitas dokumen, halaman bagian awal, urutan bab/lampiran
%%   bab/NN-*.tex      isi tiap bab (diinput berurutan dari main.tex)
%%   lampiran/NN-*.tex isi tiap lampiran
%%   gambar/           berkas gambar dokumen ini
%% Data identitas seluruh contoh ada di satu berkas: ../identitas.tex (dipakai bersama oleh
%% contoh proposal, laporan, maupun repositori).
%% Rujukan sistematika menurut panduan: {hal}
%% Kompilasi dari direktori ini: ../../skrip/build.sh --only={nama} (dari akar repo), atau cukup
%% Ctrl+S bila disunting di code-server/VS Code — .vscode/settings.json menyetel TEXINPUTS,
%% BSTINPUTS, dan BIBINPUTS ke akar repo supaya kelas, paket, bst, pustaka, dan logo terjangkau.
\\documentclass[{opsi},logodir=../../logo,logo=logo-unnes]{{unnes-ta}}

%% Data identitas bersama diambil dari ../identitas.tex. Baris di bawah hanya menambah atau
%% menimpa data bersama itu untuk dokumen ini (judul, gelar, pembimbing/penguji tambahan).
\\input{{../identitas}}
\\identitas{{
{identitas}
}}
"""

# ======================================================== blok bagian awal
BAGIAN_AWAL_LAPORAN = r"""
\begin{document}
\bagianawal

\sampul
\halamanjudul
\punggung

\persetujuanpembimbing
\pengeshantimpenguji
\pernyataankeaslian

\motopersembahan{%
  \begin{center}
    ``Ilmu tanpa amal bagaikan pohon tanpa buah.''\\[0.4cm]
    \textit{(pepatah)}
  \end{center}
  \vspace{0.6cm}
  \noindent Persembahan: karya ini dipersembahkan untuk kedua orang tua, keluarga, dan
  almamater Universitas Negeri Semarang.
}

\abstrak[{katakunci}]{%
{abstrak}
}

\abstracten[translated keywords]{%
  This final project reports the design and the evaluation of the work described in
  the Indonesian abstract. The study was carried out in Semarang in 2026 and the results
  indicate that the proposed approach meets the intended objectives.
}

\begin{prakata}
Puji syukur penulis panjatkan atas selesainya penyusunan tugas akhir ini. Ucapan terima
kasih disampaikan kepada dosen pembimbing, mitra kegiatan, keluarga, serta rekan mahasiswa
yang telah membantu kelancaran penyusunan karya ini.
\end{prakata}
\tandatanganprakata{penulis}

\daftarisi
\daftargambar
\daftartabel

\daftaristilah{%
  \istilah{Kata kunci pertama}{penjelasan singkat istilah}
  \istilah{Kata kunci kedua}{penjelasan singkat istilah}
}

\daftarlampiran
"""

BAGIAN_AWAL_PROPOSAL = r"""
\begin{document}
\bagianawal

\sampul
\halamanjudul

\persetujuanpembimbing

\daftarisi
\daftargambar
\daftartabel

\daftaristilah{%
  \istilah{Kata kunci pertama}{penjelasan singkat istilah}
  \istilah{Kata kunci kedua}{penjelasan singkat istilah}
}
"""

# ============================================================== potongan isi
TABEL = r"""
\begin{table}[htbp]
  \centering
  \caption{Ringkasan penelitian atau kegiatan terdahulu yang relevan}
  \label{tab:terdahulu}
  \begin{tabular}{clc}
    \toprule
    No & Fokus kajian & Hasil utama \\
    \midrule
    1 & Kajian pertama \citep{martin2014write} & Efektif pada ranah kognitif \\
    2 & Kajian kedua \citep{geraldi2017project} & Meningkat kategori sedang \\
    \bottomrule
  \end{tabular}
  \sumber{penulis dari berbagai sumber (2026)}
\end{table}
"""

GAMBAR = r"""
\begin{figure}[htbp]
  \centering
  \includegraphics[width=8cm]{gambar/diagram-alur}
  \caption{Alur atau sketsa kegiatan}
  \label{gam:alur}
  \sumber{Dokumentasi penulis (2026)}
\end{figure}
"""

SITASI_CONTOH = r"""
Kajian pustaka disusun dari sumber terkini \citep{creswell2018research, patten2017understanding}
dan dari pedoman resmi universitas \citep{unnes2024panduanakademik}. Regulasi penjaminan mutu
menjadi dasar kebijakan \citep{permendikbudristek2023}.
"""

# Perintah khas gaya nama-tahun; pada gaya bernomor (IEEE/ACS) kelas menolaknya.
SITASI_CONTOH_MLA = r""" Contoh rujukan gaya MLA: \citemla[23]{patten2017understanding}.
"""

DAFTAR_PUSTAKA = r"""
\bagianakhir
\daftarpustaka{../../referensi/contoh}
"""

# Mode repositori tidak memuat naskah artikel, jadi tidak ada daftar pustaka (panduan hal. 59).
AWAL_AKHIR_TANPA_PUSTAKA = r"""
\bagianakhir
"""


def bab_skripsi(mode: str, mla: bool = True) -> str:
    sitasi = SITASI_CONTOH + (SITASI_CONTOH_MLA if mla else "")
    bab34 = "" if mode == "proposal" else r"""
\chapter{HASIL DAN PEMBAHASAN}
Data dikumpulkan sesuai prosedur yang diuraikan pada bab sebelumnya, kemudian dianalisis dan
dibahas dengan teori yang digunakan. Tabel dan gambar disajikan berurutan sesuai urutan
pembicaraan, dan setiap tabel diberi sumber.

\chapter{PENUTUP}
\section{Simpulan}
Simpulan memuat jawaban atas pertanyaan penelitian yang telah dirumuskan pada bab pendahuluan.

\section{Saran}
Saran ditujukan kepada pihak terkait, peneliti lanjutan, dan pemanfaat hasil penelitian.
"""
    return r"""
\chapter{PENDAHULUAN}
\section{Latar Belakang}
Kondisi nyata yang ditemui di lapangan belum sesuai dengan kondisi yang diharapkan, sehingga
topik ini penting dan layak diteliti. Uraian diawali dengan fenomena yang ditemui peneliti,
didukung penelitian terdahulu, lalu menunjukkan kesenjangan dan kebaruan penelitian.
""" + sitasi + TABEL + r"""
\section{Rumusan Masalah}
Rumusan masalah dituliskan singkat, padat, dan sistematis dalam bentuk pertanyaan penelitian.

\section{Tujuan Penelitian}
Tujuan penelitian menyatakan upaya penyelesaian masalah yang diuraikan pada rumusan masalah.

\section{Manfaat Penelitian}
Manfaat teoretis berupa sumbangan bagi pengembangan keilmuan, sedangkan manfaat praktis
diarahkan pada pemanfaat hasil penelitian.

\section{Kebaruan Penelitian}
Kebaruan penelitian dijelaskan melalui perbedaan dibandingkan penelitian terdahulu, baik pada
konsep, konteks, metode, maupun penerapannya.

\chapter{KAJIAN PUSTAKA}
\section{Tinjauan Pustaka}
Tinjauan pustaka menguraikan rangkaian hasil penelitian lain yang menjadi landasan penelitian,
bukan sekadar daftar penelitian.

\section{Landasan Teoretik}
Landasan teoretik memuat konstruksi teori atau konsep yang mendasari pembahasan.
""" + GAMBAR + r"""
\chapter{METODE PENELITIAN}
\section{Pendekatan, Jenis, dan Prosedur Penelitian}
Dijelaskan pendekatan dan jenis penelitian, tahapan, prosedur, luaran, serta indikator capaian
yang terukur di setiap tahapan.

\section{Lokasi dan Waktu Penelitian}
Penelitian dilaksanakan di lokasi dan rentang waktu yang dijelaskan pada subbab ini.

\section{Subjek Penelitian/Sampel dan Populasi}
Subjek penelitian beserta teknik pengambilannya dijelaskan secara rinci.

\section{Data dan Sumber Data}
Jenis data serta sumber data primer dan sekunder dijelaskan pada subbab ini.

\section{Teknik Pengumpulan Data}
Instrumen pengumpulan data dilampirkan secara lengkap pada bagian lampiran.

\section{Teknik Keabsahan Data}
Uji keabsahan data dilakukan sesuai pendekatan penelitian yang digunakan.

\section{Teknik Analisis Data}
Analisis data mengikuti tahapan pengolahan data sesuai jenis penelitian yang dipilih.
""" + bab34


def bab_proyek(mode: str, mla: bool = True) -> str:
    sitasi = SITASI_CONTOH + (SITASI_CONTOH_MLA if mla else "")
    bab45 = "" if mode == "proposal" else r"""
\chapter{HASIL DAN PEMBAHASAN}
Pelaksanaan proyek beserta hasil, capaian, dan dampaknya bagi masyarakat sasaran diuraikan pada
bab ini, dilengkapi dokumentasi kegiatan.

\chapter{PENUTUP}
\section{Simpulan}
\section{Saran}
"""
    return r"""
\chapter{PENDAHULUAN}
\section{Gambaran Umum Masyarakat Sasaran}
Masyarakat sasaran beserta kondisi sosial ekonominya diuraikan pada subbab ini.
""" + sitasi + r"""
\section{Permasalahan}
Permasalahan yang dihadapi masyarakat sasaran diuraikan berdasarkan hasil observasi awal.

\section{Solusi Pemecahan Masalah}
Solusi yang ditawarkan disertai keunggulan dan kelemahannya. Mitra kegiatan sepakat
berkolaborasi seperti tertuang pada lampiran.

\section{Tujuan Proyek}
\section{Kontribusi Proyek bagi Masyarakat Sasaran}
""" + TABEL + r"""
\chapter{KAJIAN PUSTAKA}
\section{Tinjauan Pustaka}
Tinjauan pustaka memuat temuan penelitian atau proyek lain dari artikel, laporan kegiatan,
buku, dan sumber terpercaya lainnya.

\section{Landasan Teoretik}
\chapter{METODE PELAKSANAAN}
\section{Pendekatan Pelaksanaan Proyek}
\section{Lokasi dan Waktu Pelaksanaan}
\section{Mitra yang Terlibat}
\section{Prosedur Pelaksanaan Proyek}
\section{Penerapan IPTEKS}
""" + GAMBAR + r"""
\section{Teknik Monitoring dan Evaluasi Proyek}
Indikator capaian yang terukur disusun untuk setiap tahapan pelaksanaan proyek.
""" + bab45


def bab_prototipe(mode: str, mla: bool = True) -> str:
    sitasi = SITASI_CONTOH + (SITASI_CONTOH_MLA if mla else "")
    bab45 = "" if mode == "proposal" else r"""
\chapter{HASIL DAN PEMBAHASAN}
Prototipe yang dihasilkan beserta hasil uji kelayakan dan potensi dampaknya diuraikan pada bab
ini, dilengkapi dokumentasi purwarupa.

\chapter{PENUTUP}
\section{Simpulan}
\section{Saran}
"""
    return r"""
\chapter{PENDAHULUAN}
\section{Latar Belakang}
Urgensi perancangan prototipe diuraikan dengan dukungan literatur dan data pendukung.
""" + sitasi + r"""
\section{Rumusan Masalah}
Permasalahan yang akan dipecahkan melalui prototipe dituliskan dalam bentuk pernyataan atau
kalimat tanya.

\section{Tujuan Prototipe}
\section{Manfaat Prototipe}
\section{Potensi Dampak Fungsional/Komersial}
Potensi dampak penerapan maupun dampak komersial prototipe diuraikan pada subbab ini.

\chapter{KAJIAN PUSTAKA}
\section{Tinjauan Pustaka}
Literatur prototipe terdahulu dipakai sebagai acuan perancangan.

\section{Landasan Teoretik}
\chapter{METODE PELAKSANAAN}
\section{Pendekatan Perancangan}
\section{Lokasi dan Waktu}
\section{Prosedur Perancangan}
""" + TABEL + GAMBAR + r"""
\section{Teknik Perancangan}
\section{Teknik Uji Kelayakan Hasil}
Indikator capaian yang terukur di setiap tahapan disertakan pada subbab ini.
""" + bab45


def bab_publikasi(mode: str, nama: str, mla: bool = True) -> str:
    sitasi = SITASI_CONTOH + (SITASI_CONTOH_MLA if mla else "")
    if mode == "repositori":
        return r"""
\chapter{TAUTAN DAN KETERANGAN PUBLIKASI}
\section{Tautan Homepage Jurnal}
Tautan homepage jurnal: \url{https://contoh-jurnal.unnes.ac.id/index.php/contoh}

\section{Keterangan Acceptance}
Nama jurnal, tautan homepage jurnal, keterangan volume, nomor, dan tahun terbit dicatat pada
subbab ini beserta bukti \textit{accepted} (letter of acceptance) yang dilampirkan.
"""
    if mode == "laporan":
        return r"""
\chapter{NASKAH ARTIKEL ILMIAH}
Naskah artikel pada bagian ini disusun mengikuti template manuskrip jurnal tujuan, bukan
sistematika bab skripsi. Berkas terpisah naskah (berkas .docx atau .pdf) dilampirkan bersama
letter of acceptance, tautan homepage jurnal, dan bukti korespondensi dengan editor.

\section{Judul Artikel}
\section{Abstrak}
\section{Pendahuluan}
Naskah artikel memuat sitasi mengikuti gaya jurnal tujuan, misalnya:""" + sitasi + r"""
\section{Metode}
\section{Hasil dan Pembahasan}
\section{Simpulan}
\section{Ucapan Terima Kasih}
"""
    return r"""
\chapter{PENDAHULUAN}
\section{Latar Belakang}
\section{Rumusan Masalah}
Pertanyaan penelitian dituliskan singkat, padat, dan sistematis sebagai dasar penyusunan artikel.
""" + sitasi + r"""
\section{Tujuan}
Tujuan penulisan artikel dipastikan terjawab pada abstrak, pembahasan, dan simpulan.

\section{Manfaat}
\section{Kebaruan}
Kebaruan dijelaskan melalui pemetaan area penelitian dan posisi studi ini di dalamnya.

\chapter{TINJAUAN PUSTAKA}
Petakan dan nilai area penelitian untuk menyadarkan urgensi serta membenarkan pertanyaan ilmiah.
Utamakan pustaka dari jurnal bereputasi.

\chapter{METODE}
Subbab pada bab ini ditentukan oleh dosen pembimbing bersama mahasiswa sesuai kebutuhan dan
karakteristik studi.
""" + TABEL


def bab_prestasi(mla: bool = True) -> str:
    sitasi = SITASI_CONTOH + (SITASI_CONTOH_MLA if mla else "")
    return r"""
\chapter{PENDAHULUAN}
\section{Latar Belakang}
Alasan dan kondisi yang melatarbelakangi karya tulis ilmiah serta partisipasi pada cabang
kejuaraan diuraikan dari perspektif bidang ilmu.
""" + sitasi + r"""
\section{Tujuan Kegiatan}
\section{Manfaat Kegiatan}
\chapter{LANDASAN TEORETIK}
Konsep atau teori yang mendasari pembahasan diuraikan sesuai cabang kejuaraan yang diikuti.
""" + GAMBAR + r"""
\chapter{METODE PELAKSANAAN KEGIATAN}
\section{Strategi yang Dilakukan}
Strategi pada saat latihan maupun perlombaan, termasuk peran pembimbing, diuraikan pada subbab ini.

\section{Waktu dan Tempat Kegiatan}
\section{Sarana dan Prasarana Kegiatan}
\chapter{HASIL KEGIATAN DAN PEMBAHASAN}
Refleksi terhadap kejuaraan yang telah diikuti diuraikan berdasarkan bidang ilmu masing-masing,
dilengkapi dokumentasi dan sertifikat pada lampiran.
"""


# =============================================================== lampiran
LAMPIRAN = {
    "skripsi": r"""\lampiraninstrumen
\lampiranbuktiizinpenelitian
\lampiranizinetik
\lampiranskpembimbing
\lampiranskpenguji
""",
    "proyek": r"""\lampiranmitra
\lampiranpernyataankomitmen
\lampiransketsa
\lampiranluaranhki
\lampiranmedia
\lampirandokumentasi
\lampiranskpembimbing
""",
    "prototipe": r"""\lampiransketsa
\lampiranluaranhki
\lampiranmedia
\lampirandokumentasi
\lampiranskpembimbing
""",
    "publikasi": r"""\lampiranloa
\lampiranhomepagejurnal
\lampirankorespondensi
\lampiranbuktiizinpenelitian
""",
    "prestasi": r"""\lampiransertifikatprestasi
\lampiranpemberitaanmedia
\lampirandokumentasi
\lampiranskpembimbing
""",
}

BIODATA = r"""\biodatapenulis{%
  \textbf{Riwayat Pendidikan}\par
  \begin{enumerate}
    \item SD Negeri Contoh, lulus tahun 2016.
    \item SMP Negeri Contoh, lulus tahun 2019.
    \item SMA Negeri Contoh, lulus tahun 2022.
    \item Universitas Negeri Semarang, Program Studi Pendidikan Teknik Informatika.
  \end{enumerate}
}
"""

ABSTRAK_UMUM = """  Tugas akhir ini disusun untuk menjawab rumusan masalah yang telah ditetapkan. Pendekatan
  yang digunakan diuraikan pada bab metode, sedangkan hasil dan pembahasannya disajikan pada
  bab hasil dan pembahasan. Simpulan memuat jawaban atas tujuan yang telah dirumuskan."""


URUTAN_KUNCI = [
    "judul", "nama", "nim", "prodi", "fakultas", "gelar", "kota", "tahun",
    "pembimbinga", "pembimbinganip", "pembimbingb", "pembimbingbnip",
    "ketua", "ketuanip", "sekretaris", "sekretarisnip",
    "penguji1", "penguji1nip", "penguji2", "penguji2nip", "penguji3", "penguji3nip",
    "hari", "tanggal", "tanggalpersetujuan", "tanggalpernyataan",
    "tempatlahir", "tanggallahir", "alamat", "surel",
]


def identitas(judul: str, tambahan: str = "", pembimbing: str = "", ketua: str = "") -> str:
    """Menyusun blok \\identitas dengan urutan kunci yang tetap (rapi dibaca)."""
    nilai = {
        "judul": judul,
        "nama": "Nama Mahasiswa",
        "nim": "1234567890",
        "prodi": "Pendidikan Teknik Informatika",
        "fakultas": "Fakultas Teknik",
        "gelar": "Sarjana Pendidikan",
        "tahun": "2026",
        "pembimbinga": "Dr. Pembimbing Satu, M.Kom.",
        "pembimbinganip": "198001012005011001",
        "ketua": "Prof. Dr. Ketua Penguji, M.Pd.",
        "ketuanip": "196001011990031001",
        "sekretaris": "Dr. Sekretaris Penguji, M.Kom.",
        "sekretarisnip": "197002022000031002",
        "penguji1": "Dr. Penguji Satu, M.Pd.",
        "penguji1nip": "197503032005012003",
        "penguji2": "Dr. Penguji Dua, M.Kom.",
        "penguji2nip": "198004042010011004",
        "hari": "Senin",
        "tanggal": "12 Januari",
        "tanggalpersetujuan": "10 Januari 2026",
        "tanggalpernyataan": "10 Januari 2026",
        "tempatlahir": "Semarang",
        "tanggallahir": "1 Januari 2004",
        "alamat": "Jalan Contoh Nomor 1, Sekaran, Gunungpati, Semarang",
        "surel": "nama.mahasiswa@students.unnes.ac.id",
    }
    for tambahan_blok in (pembimbing, ketua, tambahan):
        for baris in tambahan_blok.splitlines():
            if "=" in baris:
                kunci, _, isi = baris.partition("=")
                nilai[kunci.strip().lstrip("%").strip()] = isi.strip().rstrip(",")
    lebar = max(len(k) for k in nilai)
    keluaran = [f"  {k:<{lebar}} = {{{nilai[k]}}}," for k in URUTAN_KUNCI if nilai.get(k)]
    sisa = [k for k in nilai if k not in URUTAN_KUNCI]
    keluaran += [f"  {k:<{lebar}} = {{{nilai[k]}}}," for k in sisa]
    return "\n".join(keluaran)


DUA_PEMBIMBING = """  pembimbingb    = {Dr. Pembimbing Dua, M.Pd.},
  pembimbingbnip = {198502022010012002},"""
PENGUJI3 = """  penguji3     = {Dr. Pembimbing Satu, M.Kom.},
  penguji3nip  = {198001012005011001},"""

# ================================================ data identitas (satu sumber)
# Data bersama seluruh contoh ditulis ke contoh/data/identitas-umum.tex. Setiap dokumen
# mengambil berkas itu lalu menambah atau menimpa kunci yang khusus dokumen tersebut.
IDENTITAS_UMUM = r"""%% Data identitas bersama seluruh dokumen di contoh/ (satu sumber di akar contoh/).
%% Dipakai semua contoh lewat identitas.tex masing-masing: proposal, laporan, maupun
%% repositori hanya menambah atau menimpa kunci yang khusus dokumen itu (judul, pembimbing
%% kedua, gelar). Cukup ubah berkas ini sekali untuk mengganti data pada semua contoh.
\identitas{
  nama               = {Nama Mahasiswa},
  nim                = {1234567890},
  prodi              = {Pendidikan Teknik Informatika},
  fakultas           = {Fakultas Teknik},
  kota               = {Semarang},
  tahun              = {2026},
  pembimbinga        = {Dr. Pembimbing Satu, M.Kom.},
  pembimbinganip     = {198001012005011001},
  ketua              = {Prof. Dr. Ketua Penguji, M.Pd.},
  ketuanip           = {196001011990031001},
  sekretaris         = {Dr. Sekretaris Penguji, M.Kom.},
  sekretarisnip      = {197002022000031002},
  penguji1           = {Dr. Penguji Satu, M.Pd.},
  penguji1nip        = {197503032005012003},
  penguji2           = {Dr. Penguji Dua, M.Kom.},
  penguji2nip        = {198004042010011004},
  hari               = {Senin},
  tanggal            = {12 Januari},
  tanggalpersetujuan = {10 Januari 2026},
  tanggalpernyataan  = {10 Januari 2026},
  tempatlahir        = {Semarang},
  tanggallahir       = {1 Januari 2004},
  alamat             = {Jalan Contoh Nomor 1, Sekaran, Gunungpati, Semarang},
  surel              = {nama.mahasiswa@students.unnes.ac.id}
}
"""

GELAR = {"sarjana": "Sarjana Pendidikan", "diploma": "Ahli Madya"}


def data_dokumen(judul: str, jenjang: str = "sarjana", tambahan: str = "") -> str:
    r"""Baris kunci identitas untuk dokumen ini (menimpa data bersama di contoh/identitas.tex)."""
    baris = [f"  judul  = {{{judul}}},",
             f"  gelar  = {{{GELAR[jenjang]}}},"]
    for baris_tambahan in tambahan.splitlines():
        if "=" in baris_tambahan:
            baris.append("  " + baris_tambahan.strip().lstrip("%").strip())
    return "\n".join(baris)


def slug(teks: str) -> str:
    """Nama berkas dari judul bagian: huruf kecil, spasi dan tanda baca jadi tanda hubung."""
    teks = re.sub(r"[^a-z0-9]+", "-", teks.lower()).strip("-")
    return teks or "bagian"


def bagi_bab(isi: str) -> list[tuple[str, str]]:
    """Memecah isi bagian utama menjadi daftar (nama berkas, isi) per bab."""
    potongan = [b for b in re.split(r"(?m)^(?=\\chapter\{)", isi) if b.strip()]
    hasil = []
    for i, bagian in enumerate(potongan, 1):
        judul = re.search(r"\\chapter\{([^}]*)\}", bagian)
        nama = slug(judul.group(1)) if judul else f"bab-{i}"
        hasil.append((f"{i:02d}-{nama}", bagian.strip() + "\n"))
    return hasil


# Nama berkas lampiran supaya mudah dibaca (perintah \lampiranxxx -> berkas).
LAMPIRAN_NAMA = {
    "instrumen": "instrumen-penelitian",
    "buktiizinpenelitian": "bukti-izin-penelitian",
    "izinetik": "izin-etik",
    "skpembimbing": "sk-pembimbing",
    "skpenguji": "sk-penguji",
    "mitra": "pernyataan-kesediaan-mitra",
    "pernyataankomitmen": "pernyataan-komitmen",
    "sketsa": "draf-karya-sketsa",
    "luaranhki": "luaran-hki",
    "media": "publikasi-media",
    "dokumentasi": "dokumentasi",
    "loa": "letter-of-acceptance",
    "homepagejurnal": "homepage-jurnal",
    "korespondensi": "bukti-korespondensi",
    "sertifikatprestasi": "sertifikat-prestasi",
    "pemberitaanmedia": "pemberitaan-media",
}


def bagi_lampiran(isi: str) -> list[tuple[str, str]]:
    """Memecah daftar perintah lampiran menjadi daftar (nama berkas, isi) per lampiran."""
    posisi = [m.start() for m in re.finditer(r"(?m)^\\lampiran[a-z]*(?=\{|$|\s)", isi)]
    hasil = []
    for i, mulai in enumerate(posisi, 1):
        akhir = posisi[i] if i < len(posisi) else len(isi)
        bagian = isi[mulai:akhir].strip()
        if not bagian:
            continue
        perintah = re.match(r"\\lampiran([a-z]*)", bagian).group(1)
        judul = re.search(r"\{([^}]*)\}", bagian)
        nama = (slug(judul.group(1)) if judul
                else LAMPIRAN_NAMA.get(perintah, slug(perintah) if perintah else f"lampiran-{i}"))
        hasil.append((f"{i:02d}-{nama}", bagian + "\n"))
    return hasil


# ================================================================ gambar contoh
GAMBAR_SUMBER = r"""%% Gambar contoh: alur tiga tahap, digambar dengan perintah dasar LaTeX.
%% Berkas ini dikompilasi menjadi diagram-alur.pdf lalu dipakai bab lewat
%% \includegraphics[width=8cm]{gambar/diagram-alur}. Ganti dengan gambar Anda.
\documentclass[10pt]{article}
\usepackage[paperwidth=9cm,paperheight=2.3cm,margin=2mm]{geometry}
\usepackage{mathptmx}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\begin{document}
\centering
\framebox[2.2cm]{\parbox[c][1cm][c]{2cm}{\centering\scriptsize Identifikasi\\ masalah}}
\hspace{0.15cm}\small$\longrightarrow$\hspace{0.15cm}
\framebox[2.2cm]{\parbox[c][1cm][c]{2cm}{\centering\scriptsize Rancangan\\ solusi}}
\hspace{0.15cm}\small$\longrightarrow$\hspace{0.15cm}
\framebox[2.2cm]{\parbox[c][1cm][c]{2cm}{\centering\scriptsize Uji coba\\ dan evaluasi}}
\end{document}
"""


def tulis_gambar(direktori: pathlib.Path) -> None:
    """Menulis gambar contoh (berkas sumber + PDF) di contoh/<nama>/gambar/."""
    folder = direktori / "gambar"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "diagram-alur.tex").write_text(GAMBAR_SUMBER, encoding="utf-8")
    hasil = subprocess.run(["pdflatex", "-interaction=nonstopmode", "diagram-alur.tex"],
                           cwd=folder, capture_output=True, text=True)
    for sisa in ("diagram-alur.aux", "diagram-alur.log"):
        (folder / sisa).unlink(missing_ok=True)
    if not (folder / "diagram-alur.pdf").exists():
        raise SystemExit("gambar contoh gagal dikompilasi:\n" + hasil.stdout[-400:])


# ========================================================= rujukan halaman panduan
HAL = {
    "skripsi": "hal. 14-15 (proposal), hal. 16-18 (laporan)",
    "proyek": "hal. 29-31 (proposal), hal. 31-33 (laporan)",
    "prototipe": "hal. 43-45 (proposal), hal. 45-46 (laporan)",
    "publikasi": "hal. 57-58 (proposal), hal. 58-60 (laporan dan repositori)",
    "prestasi": "hal. 72-74 (laporan penyetaraan)",
}


# ================================================================== daftar contoh
# nama, ket, opsi kelas, judul, bagian awal (l/p), isi bab, lampiran, biodata, opsi identitas
CONTOH = [
    ("skripsi-laporan", "skripsi laporan, jenjang sarjana, dua pembimbing",
     "jenis=skripsi,mode=laporan,jenjang=sarjana,sitasi=apa", "laporan",
     "Pengembangan Media Pembelajaran Berbasis Augmented Reality untuk Meningkatkan Hasil "
     "Belajar Siswa Sekolah Menengah Kejuruan",
     "skripsi", bab_skripsi("laporan"), True, DUA_PEMBIMBING + "\n" + PENGUJI3),
    ("skripsi-proposal", "skripsi proposal, jenjang sarjana",
     "jenis=skripsi,mode=proposal,jenjang=sarjana,sitasi=apa", "proposal",
     "Pengembangan Media Pembelajaran Berbasis Augmented Reality untuk Meningkatkan Hasil "
     "Belajar Siswa Sekolah Menengah Kejuruan",
     "skripsi", bab_skripsi("proposal"), False, DUA_PEMBIMBING),
    ("proyek-laporan", "proyek laporan, jenjang sarjana, dengan mitra",
     "jenis=proyek,mode=laporan,jenjang=sarjana,sitasi=apa", "laporan",
     "Pendampingan Digitalisasi Pemasaran Produk Unggulan Desa Menuju Pasar Digital",
     "proyek", bab_proyek("laporan"), True, DUA_PEMBIMBING),
    ("proyek-proposal", "proyek proposal, jenjang sarjana, dengan mitra",
     "jenis=proyek,mode=proposal,jenjang=sarjana,sitasi=apa", "proposal",
     "Pendampingan Digitalisasi Pemasaran Produk Unggulan Desa Menuju Pasar Digital",
     "proyek", bab_proyek("proposal"), False, DUA_PEMBIMBING),
    ("prototipe-laporan", "prototipe laporan, jenjang diploma",
     "jenis=prototipe,mode=laporan,jenjang=diploma,sitasi=ieee", "laporan",
     "Rancang Bangun Alat Monitoring Kualitas Air Kolam Budi Daya Berbasis Internet of Things",
     "prototipe", bab_prototipe("laporan", mla=False), True, ""),
    ("prototipe-proposal", "prototipe proposal, jenjang diploma",
     "jenis=prototipe,mode=proposal,jenjang=diploma,sitasi=ieee", "proposal",
     "Rancang Bangun Alat Monitoring Kualitas Air Kolam Budi Daya Berbasis Internet of Things",
     "prototipe", bab_prototipe("proposal", mla=False), False, ""),
    ("publikasi-laporan", "publikasi ilmiah laporan: bagian utama berupa naskah artikel",
     "jenis=publikasi,mode=laporan,jenjang=sarjana,sitasi=apa", "laporan",
     "Pengaruh Model Pembelajaran Berbasis Proyek terhadap Kemampuan Berpikir Kritis Mahasiswa",
     "publikasi", bab_publikasi("laporan", "publikasi-laporan"), True, DUA_PEMBIMBING),
    ("publikasi-proposal", "publikasi ilmiah proposal: artikel ilmiah yang akan diterbitkan",
     "jenis=publikasi,mode=proposal,jenjang=sarjana,sitasi=apa", "proposal",
     "Pengaruh Model Pembelajaran Berbasis Proyek terhadap Kemampuan Berpikir Kritis Mahasiswa",
     "publikasi", bab_publikasi("proposal", "publikasi-proposal"), False, DUA_PEMBIMBING),
    ("publikasi-repositori", "publikasi ilmiah versi repositori: tanpa isi artikel (panduan hal. 59)",
     "jenis=publikasi,mode=repositori,jenjang=sarjana,sitasi=apa", "laporan",
     "Pengaruh Model Pembelajaran Berbasis Proyek terhadap Kemampuan Berpikir Kritis Mahasiswa",
     "publikasi", bab_publikasi("repositori", "publikasi-repositori"), True, DUA_PEMBIMBING),
    ("prestasi-laporan", "penyetaraan prestasi kejuaraan (panduan hal. 72-74)",
     "jenis=prestasi,mode=laporan,jenjang=sarjana,sitasi=apa", "laporan",
     "Penyetaraan Prestasi Kejuaraan Nasional Bidang Rekayasa Perangkat Lunak",
     "prestasi", bab_prestasi(), True, DUA_PEMBIMBING),
    ("prestasi-proposal", "penyetaraan prestasi dalam bentuk berkas proposal (panduan hal. 8: "
                          "penyetaraan tidak memerlukan proposal)",
     "jenis=prestasi,mode=proposal,jenjang=sarjana,sitasi=apa", "proposal",
     "Penyetaraan Prestasi Kejuaraan Nasional Bidang Rekayasa Perangkat Lunak",
     "prestasi", bab_prestasi(), False, DUA_PEMBIMBING),
]


def main():
    akar = pathlib.Path(__file__).resolve().parent.parent
    tujuan = akar / "contoh"
    (tujuan / "identitas.tex").write_text(IDENTITAS_UMUM, encoding="utf-8")
    shutil.rmtree(tujuan / "data", ignore_errors=True)      # susunan lama

    tanpa_pustaka = {"publikasi-repositori"}
    jumlah_bab = jumlah_lampiran = 0
    for nama, ket, opsi, jenisbagian, judul, jenislampiran, isibab, biodata, tambahan in CONTOH:
        jenjang = "diploma" if "jenjang=diploma" in opsi else "sarjana"
        direktori = tujuan / nama
        for sub in ("bab", "lampiran", "gambar"):
            folder = direktori / sub
            folder.mkdir(parents=True, exist_ok=True)
            for lama in folder.glob("*.tex"):      # hindari berkas dari penamaan lama
                lama.unlink()

        (direktori / "identitas.tex").unlink(missing_ok=True)   # susunan lama: satu berkas saja

        bab = bagi_bab(isibab)
        for berkas, isi in bab:
            (direktori / "bab" / f"{berkas}.tex").write_text(
                f"%% {berkas}.tex — bab dokumen contoh {nama} ({HAL[jenislampiran]}).\n" + isi,
                encoding="utf-8")

        lampiran = bagi_lampiran(LAMPIRAN[jenislampiran])
        if biodata:
            lampiran.append(("99-biodata-penulis", BIODATA))
        for berkas, isi in lampiran:
            (direktori / "lampiran" / f"{berkas}.tex").write_text(
                f"%% {berkas}.tex — lampiran dokumen contoh {nama}.\n" + isi, encoding="utf-8")

        tulis_gambar(direktori)

        bagian_awal = BAGIAN_AWAL_LAPORAN if jenisbagian == "laporan" else BAGIAN_AWAL_PROPOSAL
        isi_main = (KEPALA.format(nama=nama, ket=ket, opsi=opsi, hal=HAL[jenislampiran],
                                  identitas=data_dokumen(judul, jenjang=jenjang,
                                                         tambahan=tambahan))
                    + bagian_awal.replace("{katakunci}", "media pembelajaran, hasil belajar")
                                 .replace("{abstrak}", ABSTRAK_UMUM)
                    + "\n\\bagianutama\n\n"
                    + "".join(f"\\input{{bab/{berkas}}}\n" for berkas, _ in bab)
                    + (AWAL_AKHIR_TANPA_PUSTAKA if nama in tanpa_pustaka else DAFTAR_PUSTAKA)
                    + "".join(f"\n\\input{{lampiran/{berkas}}}\n" for berkas, _ in lampiran)
                    + "\n\\end{document}\n")
        (direktori / "main.tex").write_text(isi_main, encoding="utf-8")
        jumlah_bab += len(bab)
        jumlah_lampiran += len(lampiran)

    print(f"{len(CONTOH)} dokumen contoh ditulis ke {tujuan} "
          f"({jumlah_bab} berkas bab, {jumlah_lampiran} berkas lampiran, "
          f"data bersama di contoh/identitas.tex)")

    # Setelan LaTeX Workshop ditulis ulang supaya setiap dokumen tetap bisa dikompilasi dari
    # direktorinya sendiri (TEXINPUTS/BSTINPUTS/BIBINPUTS ke akar repo). Lihat siapkan-vscode.py.
    subprocess.run([sys.executable, str(akar / "skrip" / "siapkan-vscode.py")], check=False)


if __name__ == "__main__":
    main()
