#!/usr/bin/env python3
"""Memeriksa kesebelas dokumen contoh di contoh/ (todo t61-t610).

Jalankan:  python3 uji/cek-contoh.py     (setelah skrip/build.sh)

Yang diperiksa tiap contoh:
  1. PDF ada, log 0 galat, dan bibliografi benar-benar terbentuk (isi .bbl >= 3 entri);
  2. urutan halaman bagian awal sesuai panduan untuk mode laporan / proposal;
  3. bab bagian utama sesuai jenis TA (nomor dan jumlahnya);
  4. bagian akhir: DAFTAR PUSTAKA, jumlah lampiran sesuai jenis, BIODATA PENULIS pada laporan;
  5. ukuran A4 dan margin kiri/kanan 4 cm/3 cm pada halaman isi.
"""
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
CONTOH = AKAR / "contoh"
A4 = (595.276, 841.89)
MARGIN_KIRI, MARGIN_KANAN = 113.386, 85.04   # 4 cm / 3 cm dalam pt

# nama: (mode, jenis, urutan bab yang diharapkan, jumlah lampiran minimal, biodata)
HARAP = {
    "skripsi-laporan":   ("laporan", 5, 5, True),
    "skripsi-proposal":  ("proposal", 3, 0, False),
    "proyek-laporan":    ("laporan", 5, 6, True),
    "proyek-proposal":   ("proposal", 3, 0, False),
    "prototipe-laporan": ("laporan", 5, 5, True),
    "prototipe-proposal": ("proposal", 3, 0, False),
    "publikasi-laporan": ("laporan", 1, 4, True),
    "publikasi-proposal": ("proposal", 3, 0, False),
    "publikasi-repositori": ("laporan", 1, 4, True),
    "prestasi-laporan":  ("laporan", 4, 4, True),
    "prestasi-proposal": ("proposal", 4, 0, False),
}

AWAL_LAPORAN = ["PERSETUJUAN PEMBIMBING", "PENGESAHAN", "PERNYATAAN", "ABSTRAK",
                "ABSTRACT", "PRAKATA", "DAFTAR ISI", "DAFTAR LAMPIRAN"]
AWAL_PROPOSAL = ["PERSETUJUAN PEMBIMBING", "DAFTAR ISI"]
TIDAK_ADA_DI_PROPOSAL = ["PENGESAHAN", "PERNYATAAN", "ABSTRAK", "PRAKATA"]


def teks(pdf: Path, halaman: int | None = None) -> str:
    cmd = ["mutool", "draw", "-F", "txt", "-o", "-", str(pdf)]
    if halaman:
        cmd.append(str(halaman))
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def halaman_pertama(pdf: Path, frasa: str, maxhal: int = 60):
    for hal in range(1, maxhal + 1):
        if frasa in teks(pdf, hal):
            return hal
    return None


def ukuran_dan_margin(pdf: Path, halaman: int):
    xml = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(pdf), str(halaman)],
                         capture_output=True, text=True).stdout
    akar = ET.fromstring(xml)
    hlm = akar.find("page")
    lebar, tinggi = float(hlm.get("width")), float(hlm.get("height"))
    x0 = min(float(l.get("bbox").split()[0]) for l in hlm.iter("line") if l.get("bbox"))
    x1 = max(float(l.get("bbox").split()[2]) for l in hlm.iter("line") if l.get("bbox"))
    return lebar, tinggi, x0 - MARGIN_KIRI, x1 - (lebar - MARGIN_KANAN)


def main() -> int:
    gagal = 0
    for nama, (mode, njab, nlampiran, biodata) in HARAP.items():
        direktori = CONTOH / nama
        pdf, log = direktori / "main.pdf", direktori / "main.log"
        masalah = []
        if not log.exists():
            print(f"[LEWAT] {nama}: main.log tidak ada")
            gagal += 1
            continue
        galat = re.findall(r"^! .*", log.read_text(errors="ignore"), re.M)
        if galat:
            masalah.append(f"{len(galat)} galat: {galat[0][:70]}")
        if not pdf.exists():
            masalah.append("main.pdf tidak ada")
            gagal += bool(masalah)
            continue

        isi = teks(pdf)
        # ---- bibliografi
        bbl = direktori / "main.bbl"
        entri = bbl.read_text(errors="ignore").count("bibitem") if bbl.exists() else 0
        if nama != "publikasi-repositori" and entri < 3:
            masalah.append(f"bibliografi hanya {entri} entri (bibtex belum dijalankan?)")
        if nama != "publikasi-repositori" and "DAFTAR PUSTAKA" not in isi:
            masalah.append("DAFTAR PUSTAKA tidak ada")
        # ---- bagian awal
        urutan = AWAL_LAPORAN if mode == "laporan" else AWAL_PROPOSAL
        posisi = []
        for frasa in urutan:
            hal = halaman_pertama(pdf, frasa)
            if hal is None:
                masalah.append(f"bagian awal: '{frasa}' tidak ditemukan")
            else:
                posisi.append((hal, frasa))
        if posisi != sorted(posisi):
            masalah.append("urutan bagian awal tidak sesuai: "
                           + ", ".join(f"{f}@h{p}" for p, f in posisi))
        if mode == "proposal":
            for frasa in TIDAK_ADA_DI_PROPOSAL:
                if halaman_pertama(pdf, frasa):
                    masalah.append(f"proposal tidak boleh memuat '{frasa}'")
        # ---- bab
        nomor = [int(n) for n in re.findall(r"^BAB (\d+)\.$", isi, re.M)]
        bab_unik = sorted(set(nomor))
        if bab_unik != list(range(1, njab + 1)):
            masalah.append(f"bab {bab_unik}, diharapkan 1..{njab}")
        # ---- bagian akhir
        lampiran = len(re.findall(r"^LAMPIRAN (\d+)$", isi, re.M))
        if nlampiran and lampiran < nlampiran:
            masalah.append(f"lampiran {lampiran}, diharapkan >= {nlampiran}")
        if biodata and "Biodata Penulis" not in isi:
            masalah.append("lampiran Biodata Penulis tidak ada")
        # ---- halaman isi: A4 dan margin
        hlm_bab = halaman_pertama(pdf, "Latar Belakang") or halaman_pertama(pdf, "TINJAUAN PUSTAKA")
        if hlm_bab:
            lebar, tinggi, selisih_kiri, selisih_kanan = ukuran_dan_margin(pdf, hlm_bab)
            if abs(lebar - A4[0]) > 1 or abs(tinggi - A4[1]) > 1:
                masalah.append(f"ukuran halaman {lebar:.1f}x{tinggi:.1f} pt, bukan A4")
            if abs(selisih_kiri) > 2 or abs(selisih_kanan) > 2:
                masalah.append(f"margin meleset {selisih_kiri:+.1f}/{-selisih_kanan:+.1f} pt "
                               "(kiri 4 cm / kanan 3 cm)")
        # catatan panduan yang wajib tertulis di berkas contoh tertentu
        catatan = {"prestasi-proposal": ("main.tex", "tidak memerlukan proposal")}
        if nama in catatan:
            berkas, frasa = catatan[nama]
            isi_tex = (direktori / berkas).read_text(errors="ignore")
            if frasa not in isi_tex:
                masalah.append(f"catatan panduan '{frasa}' tidak ada di {berkas}")
        status = "OK   " if not masalah else "GAGAL"
        print(f"[{status}] {nama:22s} {len(isi.splitlines()):5d} baris teks, bbl={entri}, "
              f"lampiran={lampiran}" + ("" if not masalah else
                                        "\n         - " + "\n         - ".join(masalah)))
        gagal += bool(masalah)
    print(f"\n{len(HARAP) - gagal}/{len(HARAP)} dokumen contoh sesuai pemeriksaan.")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
