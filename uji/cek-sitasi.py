#!/usr/bin/env python3
"""Memeriksa hasil keenam preset gaya sitasi.

Jalankan dari direktori uji/sitasi setelah semua .pdf dikompilasi (pdflatex, bibtex, pdflatex 2x):
    python3 ../cek-sitasi.py

Yang diperiksa:
  1. bentuk sitasi di dalam teks sesuai gaya (koma/tanpa koma, kurung siku, superskrip);
  2. daftar pustaka: entri ada, bernomor untuk gaya numerik, memuat DOI untuk APA;
  3. ukuran daftar pustaka meniru contoh panduan hal. 95 — indentasi menggantung 28,3 pt (1 cm),
     spasi tunggal di dalam entri (± 14,5 pt), jarak antarentri ± 20 pt;
  4. tidak ada label rusak "(author?)" pada gaya nama-tahun.
"""
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Berkas gaya yang diharapkan dipakai tiap preset (diperiksa dari berkas .blg bibtex)
BST = {
    "apa": "unnes-apalike-apa.bst", "ieee": "ieeetr.bst", "mla": "plainnat.bst",
    "chicago": "apalike.bst", "harvard": "apalike.bst", "acs": "unsrt.bst",
}

# Potongan teks yang harus ada di halaman isi (bentuk sitasi dalam teks)
TEKS = {
    "apa":     ["Creswell & Creswell (2018)", "(Martin, 2014)", "(Martin, 2014, 955)",
                "Febriani & Sugiarto", "Shils, 1993", "(Patten 23)"],
    "ieee":    ["[1]", "[2]", "955]", "[4, 5]", "[7]", "[8]"],
    "mla":     ["(Martin 2014)", "(Febriani and Sugiarto", "Shils 1993", "(Patten 23)"],
    "chicago": ["(Martin 2014)", "(Martin 2014, 955)", "(Patten 23)"],
    "harvard": ["(Martin 2014)", "(Patten 23)"],
    "acs":     ["hal yang sama2", "sejalan4,5", "dasar7 dan8"],  # angka superskrip menempel pada teks
}
# Tidak boleh muncul
TERLARANG = {
    "apa": ["(author?)", "[1]"], "mla": ["(author?)", "[1]"],
    "chicago": ["(author?)", "[1]"], "harvard": ["(author?)", "[1]"],
    "ieee": ["(author?)", "(Martin, 2014)"], "acs": ["(author?)", "(Martin, 2014)"],
}


def teks_pdf(pdf: Path, halaman: int | None = None) -> str:
    cmd = ["mutool", "draw", "-F", "txt", "-o", "-", str(pdf)]
    if halaman:
        cmd.append(str(halaman))
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def baris_pdf(pdf: Path, halaman: int):
    xml = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(pdf), str(halaman)],
                         capture_output=True, text=True).stdout
    keluaran = []
    for l in ET.fromstring(xml).iter("line"):
        x0, _, x1, y = (float(v) for v in l.get("bbox").split())
        t = "".join(c.get("c", "") for c in l.iter("char"))
        if t.strip():
            keluaran.append((y, x0, x1, t))
    return sorted(keluaran)


def halaman_daftarpustaka(pdf: Path) -> int:
    """Halaman yang benar-benar memuat entri daftar pustaka (bukan hanya judulnya)."""
    for hal in range(1, 40):
        baris = baris_pdf(pdf, hal)
        if "DAFTAR PUSTAKA" in teks_pdf(pdf, hal) and len(baris) > 6:
            return hal
    raise SystemExit(f"DAFTAR PUSTAKA tidak ditemukan di {pdf}")


def ukur(pdf: Path):
    """Kembalikan (indentasi_gantung, spasi_dalam_entri, spasi_antarentri)."""
    baris = baris_pdf(pdf, halaman_daftarpustaka(pdf))
    isi = [b for b in baris
           if len(b[3].strip()) > 2 and "PANDUAN" not in b[3]
           and b[3].strip() != "DAFTAR PUSTAKA" and not b[3].strip().isdigit()]
    awal = min(b[1] for b in isi)
    # baris entri baru: x0 dekat margin kiri; baris lanjutan menjorok
    mulai = [i for i, b in enumerate(isi) if b[1] < awal + 6]
    lanjut = [b for b in isi if b[1] >= awal + 6]
    gulung = sorted(b[1] for b in lanjut)
    gantung = (gulung[len(gulung) // 2] - awal) if gulung else 0.0
    dalam, antar = [], []
    for a, b in zip(mulai, mulai[1:]):
        for i in range(a, b - 1):
            # label bernomor ("[1]") berdiri pada baris visual yang sama dengan awal teks entri;
            # pasangan seperti itu bukan jarak antarbaris
            if abs(isi[i + 1][0] - isi[i][0]) >= 5:
                dalam.append(isi[i + 1][0] - isi[i][0])
        antar.append(isi[b][0] - isi[b - 1][0])
    def median(nilai):
        if not nilai:
            return 0.0
        nilai = sorted(nilai)
        return nilai[len(nilai) // 2]
    return gantung, median(dalam), median(antar)


def main() -> int:
    gagal = 0
    for gaya in BST:
        pdf = Path(f"{gaya}.pdf")
        masalah = []
        if not pdf.exists():
            print(f"[LEWAT] {gaya}.pdf tidak ada")
            gagal += 1
            continue
        isi = teks_pdf(pdf)
        for kata in TEKS[gaya]:
            if kata not in isi:
                masalah.append(f"teks tidak memuat: {kata!r}")
        for kata in TERLARANG[gaya]:
            if kata in isi:
                masalah.append(f"seharusnya tidak memuat: {kata!r}")
        if "DAFTAR PUSTAKA" not in isi:
            masalah.append("halaman DAFTAR PUSTAKA tidak ada")
        blg = Path(f"{gaya}.blg")
        if not blg.exists():
            masalah.append("bibtex belum dijalankan (berkas .blg tidak ada)")
        elif BST[gaya] not in blg.read_text(errors="ignore"):
            masalah.append(f"berkas gaya bibtex bukan {BST[gaya]}")
        if gaya in ("ieee", "acs"):
            if "[1]" not in isi:
                masalah.append("daftar pustaka gaya numerik tidak bernomor [1]")
        if gaya in ("apa", "mla", "chicago", "harvard") and "(author?)" in isi:
            masalah.append("label sitasi rusak: (author?)")
        if gaya == "apa":
            bbl = Path("apa.bbl").read_text(errors="ignore") if Path("apa.bbl").exists() else ""
            if "\\url{https://doi.org/10.1016/j.ijproman.2017.06.004}" not in bbl:
                masalah.append("APA: DOI sebagai tautan https://doi.org/... tidak ada di .bbl")
            if "&" not in isi:
                masalah.append("APA kehilangan pemisah '&' antarpenulis")
        if True:   # ukuran daftar pustaka berlaku untuk semua gaya
            gantung, dalam, antar = ukur(pdf)
            if not (26.5 <= gantung <= 30.5):
                masalah.append(f"indentasi menggantung {gantung:.1f} pt, diharapkan ±28,3 pt (1 cm)")
            if not (13.0 <= dalam <= 16.5):
                masalah.append(f"spasi dalam entri {dalam:.1f} pt, diharapkan ±14,5 pt (spasi tunggal)")
            if not (18.0 <= antar <= 22.5):
                masalah.append(f"spasi antarentri {antar:.1f} pt, diharapkan ±20 pt (panduan hal. 95)")
        status = "OK   " if not masalah else "GAGAL"
        print(f"[{status}] {gaya:8s} bst={BST[gaya]}"
              + ("" if not masalah else "\n         - " + "\n         - ".join(masalah)))
        gagal += bool(masalah)

    # uji negatif: \citemla pada gaya bernomor harus ditolak
    log = Path("/tmp/s-uji-citemla-salah.log")
    if log.exists():
        if "hanya untuk gaya nama-tahun" in log.read_text(errors="ignore"):
            print("[OK   ] penjaga \\citemla: memakai \\citemla di gaya bernomor ditolak")
        else:
            print("[GAGAL] penjaga \\citemla tidak memberi galat")
            gagal += 1
    print(f"\n{len(BST) - gagal}/{len(BST)} gaya sitasi sesuai pemeriksaan.")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
