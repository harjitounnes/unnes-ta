#!/usr/bin/env python3
"""Menyimpan halaman PDF sebagai PNG supaya bisa diperiksa dengan mata (todo t73).

Pemakaian:
    skrip/render.py contoh/skripsi-laporan --hal=1-6      halaman 1 sampai 6
    skrip/render.py contoh/skripsi-laporan --hal=1,5,23   halaman tertentu
    skrip/render.py contoh/*/main.pdf --hal=1             sampul setiap contoh
    skrip/render.py contoh/skripsi-laporan                halaman 1 sampai 8 (bawaan)

Hasil disimpan di hasil/<nama-dokumen>/hlm-<nomor>.png (direktori hasil/ sudah
masuk .gitignore). Resolusi bawaan 120 dpi.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
HASIL = AKAR / "hasil"


def daftar_halaman(arg: str) -> list[int]:
    halaman: list[int] = []
    for bagian in arg.split(","):
        if "-" in bagian:
            a, b = bagian.split("-", 1)
            halaman += list(range(int(a), int(b) + 1))
        elif bagian.strip():
            halaman.append(int(bagian))
    return halaman


def pdf_dari(arg: str) -> Path:
    p = Path(arg)
    if p.suffix == ".pdf":
        return p
    if p.is_dir():
        return p / "main.pdf" if (p / "main.pdf").exists() else p.with_suffix(".pdf")
    return p.with_suffix(".pdf")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    spesifikasi = next((a.split("=", 1)[1] for a in argv[1:] if a.startswith("--hal=")), "")
    halaman = daftar_halaman(spesifikasi) if spesifikasi else list(range(1, 9))
    berkas = [pdf_dari(a) for a in argv[1:] if not a.startswith("--")]
    keluaran = []
    for pdf in berkas:
        if not pdf.exists():
            print(f"tidak ada: {pdf}")
            continue
        tujuan = HASIL / pdf.parent.name
        tujuan.mkdir(parents=True, exist_ok=True)
        for h in halaman:
            berkas_png = tujuan / f"hlm-{h:02d}.png"
            hasil = subprocess.run(["mutool", "draw", "-r", "120", "-o", str(berkas_png),
                                    str(pdf), str(h)], capture_output=True, text=True)
            if berkas_png.exists():
                keluaran.append(berkas_png)
            else:
                print(f"gagal render {pdf} halaman {h}: {hasil.stderr.strip()[:80]}")
    for b in keluaran:
        print(b)
    return 0 if keluaran else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
