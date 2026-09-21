#!/usr/bin/env python3
"""Membuat dokumen uji kerangka sistematika untuk setiap kombinasi jenis x mode.

Kompilasi (dari direktori uji/sistematika):
    TEXINPUTS=../..: pdflatex -interaction=nonstopmode <berkas>.tex
"""
import pathlib

KASUS = [
    # nama berkas,            opsi kelas                                             , catatan
    ("skripsi-laporan",       "jenis=skripsi,mode=laporan",                            "bab 1-5"),
    ("skripsi-proposal",      "jenis=skripsi,mode=proposal",                           "bab 1-3 saja"),
    ("skripsi-laporan-opsional", "jenis=skripsi,mode=laporan,opsional",                "subbab 'bila ada' ikut"),
    ("proyek-laporan",        "jenis=proyek,mode=laporan",                             "bab 1-5"),
    ("proyek-proposal",       "jenis=proyek,mode=proposal",                            "bab 1-3 saja"),
    ("prototipe-laporan",     "jenis=prototipe,mode=laporan",                          "bab 1-5"),
    ("prototipe-proposal",    "jenis=prototipe,mode=proposal",                         "bab 1-3 saja"),
    ("publikasi-proposal",    "jenis=publikasi,mode=proposal",                         "bab 1-3"),
    ("publikasi-laporan",     "jenis=publikasi,mode=laporan",                          "hanya naskah artikel"),
    ("publikasi-repositori",  "jenis=publikasi,mode=repositori",                       "tautan tanpa isi artikel"),
    ("prestasi-laporan",      "jenis=prestasi,mode=laporan",                           "bab 1-4"),
    ("prestasi-proposal",     "jenis=prestasi,mode=proposal",                          "harus memberi peringatan"),
]

TEMPLATE = r"""%% Dokumen uji sistematika: {nama}
%% Kompilasi: TEXINPUTS=../..: pdflatex -interaction=nonstopmode {nama}.tex
\documentclass[{opsi},logodir=../../logo,logo=logo-placeholder]{{unnes-ta}}

\identitas{{
  judul    = {{Kerangka Sistematika: {nama}}},
  nama     = {{Nama Mahasiswa}},
  nim      = {{1234567890}},
  prodi    = {{Pendidikan Teknik Informatika}},
  fakultas = {{Fakultas Teknik}},
  tahun    = {{2026}},
  pembimbinga = {{Dr. Pembimbing Satu, M.Kom.}},
}}

\begin{{document}}
\bagianutama
\sistematika
\end{{document}}
"""


def main():
    tujuan = pathlib.Path(__file__).resolve().parent / "sistematika"
    tujuan.mkdir(exist_ok=True)
    for nama, opsi, _ in KASUS:
        (tujuan / f"{nama}.tex").write_text(
            TEMPLATE.format(nama=nama, opsi=opsi), encoding="utf-8")
    print(f"{len(KASUS)} berkas uji ditulis ke {tujuan}")


if __name__ == "__main__":
    main()
