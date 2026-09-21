#!/usr/bin/env python3
"""Membuat dokumen uji gaya sitasi untuk ketujuh varian preset (todo t51-t56).

Kompilasi tiap berkas (dari direktori uji/sitasi):
    export TEXINPUTS=../../:    BSTINPUTS=../../bst:    BIBINPUTS=../../referensi:
    pdflatex -interaction=nonstopmode <berkas>.tex
    bibtex <berkas>
    pdflatex -interaction=nonstopmode <berkas>.tex   (2x)
"""
import pathlib

GAYA = [
    ("apa",     "APA (hal. 92 butir 3a) — memakai bst/unnes-apalike-apa.bst milik template"),
    ("ieee",    "IEEE (hal. 92 butir 3b)"),
    ("mla",     "MLA (hal. 92 butir 3c)"),
    ("chicago", "Chicago (hal. 92 butir 3d)"),
    ("harvard", "Harvard (hal. 92 butir 3e)"),
    ("acs",     "ACS (hal. 92 butir 3f)"),
]

# \citemla hanya sah untuk gaya nama-tahun; pada gaya bernomor (IEEE, ACS) nilainya "(author?)".
BARIS_MLA = "Bentuk MLA diuji tersendiri \\citemla[23]{patten2017understanding}."
# \citet hanya bermakna pada gaya nama-tahun; gaya bernomor memakai \cite biasa
BARIS_AWAL = {
    "apa": "Penelitian campuran dibahas oleh \\citet{creswell2018research} secara mendalam.",
    "mla": "Penelitian campuran dibahas oleh \\citet{creswell2018research} secara mendalam.",
    "chicago": "Penelitian campuran dibahas oleh \\citet{creswell2018research} secara mendalam.",
    "harvard": "Penelitian campuran dibahas oleh \\citet{creswell2018research} secara mendalam.",
    "ieee": "Penelitian campuran dibahas pada \\cite{creswell2018research} secara mendalam.",
    "acs": "Penelitian campuran dibahas pada \\cite{creswell2018research} secara mendalam.",
}
TANPA_MLA = ("Perintah \\texttt{citemla} sengaja tidak dipakai di gaya bernomor karena berkas "
             "gaya IEEE/ACS tidak memuat daftar nama penulis; kelas akan menolaknya.")

TEMPLATE = r"""%% Uji gaya sitasi: @GAYA@ — @KET@
%% Kompilasi: TEXINPUTS=../../:../../bst: BSTINPUTS=../../bst:
%%            pdflatex @GAYA@ && bibtex @GAYA@ && pdflatex @GAYA@ (2x)
%% (direktori bst/ harus terjangkau TEXINPUTS untuk pemeriksaan berkas gaya oleh kelas,
%%  dan BSTINPUTS supaya bibtex menemukan unnes-apalike-apa.bst)
\documentclass[sitasi=@GAYA@,logodir=../../logo,logo=logo-placeholder]{unnes-ta}

\identitas{
  judul    = {Uji Gaya Sitasi @GAYA@},
  nama     = {Nama Mahasiswa},
  nim      = {1234567890},
  prodi    = {Pendidikan Teknik Informatika},
  fakultas = {Fakultas Teknik},
  tahun    = {2026},
  pembimbinga = {Dr. Pembimbing Satu, M.Kom.},
}

\begin{document}
\bagianutama

\chapter{CONTOH SITASI}
\section{Bentuk Sitasi dalam Teks}
@AWAL@
Kajian sebelumnya menegaskan hal yang sama \citep{martin2014write}.
Pendapat serupa disampaikan pada bagian tertentu \citep[955]{martin2014write}.
Rujukan bernomor mengikuti \cite{geraldi2017project}.
Dua sumber lain juga sejalan \citep{febriani2020memahami,shils1993etika}.
@MLA@
Buku metodologi seni dipakai sebagai acuan \citep{rohidi2012research}.
Regulasi akademik menjadi dasar \citep{permendikbudristek2023} dan
\citep{unnes2024panduanakademik}.

\daftarpustaka{../../referensi/contoh}

\end{document}
"""


def main():
    tujuan = pathlib.Path(__file__).resolve().parent / "sitasi"
    tujuan.mkdir(exist_ok=True)
    for gaya, ket in GAYA:
        mla = BARIS_MLA if gaya in ("apa", "mla", "chicago", "harvard") else TANPA_MLA
        isi = (TEMPLATE.replace("@AWAL@", BARIS_AWAL[gaya])
                       .replace("@GAYA@", gaya)
                       .replace("@KET@", ket)
                       .replace("@MLA@", mla))
        (tujuan / f"{gaya}.tex").write_text(isi, encoding="utf-8")
    print(f"{len(GAYA)} berkas uji ditulis ke {tujuan}")


if __name__ == "__main__":
    main()
