#!/usr/bin/env python3
"""Memeriksa kerangka sistematika setiap varian terhadap sistematika panduan.

Jalankan dari direktori uji/sistematika setelah semua berkas .pdf dikompilasi:
    python3 ../cek-sistematika.py
"""
import re
import subprocess
import sys
from pathlib import Path

# nama berkas -> (harus memuat, tidak boleh memuat)
HARAP = {
    "skripsi-laporan": (
        ["PENDAHULUAN", "KAJIAN PUSTAKA", "METODE PENELITIAN", "HASIL DAN PEMBAHASAN",
         "PENUTUP", "Latar Belakang", "Batasan" if False else "Rumusan Masalah",
         "Tujuan Penelitian", "Manfaat Penelitian", "Kebaruan Penelitian",
         "Tinjauan Pustaka", "Landasan Teoretik", "Simpulan", "Saran"],
        ["Gambaran Umum Masyarakat Sasaran", "Batasan Masalah", "Kerangka Berpikir",
         "Etika Penelitian", "NASKAH ARTIKEL ILMIAH"],
    ),
    "skripsi-proposal": (
        ["PENDAHULUAN", "KAJIAN PUSTAKA", "METODE PENELITIAN", "Teknik Analisis Data"],
        ["HASIL DAN PEMBAHASAN", "PENUTUP", "Simpulan"],
    ),
    "skripsi-laporan-opsional": (
        ["Batasan Masalah", "Kerangka Berpikir", "Hipotesis Teoretis",
         "Variabel Penelitian dan Definisi Operasional", "Hipotesis Statistik",
         "Etika Penelitian"],
        [],
    ),
    "proyek-laporan": (
        ["PENDAHULUAN", "KAJIAN PUSTAKA", "METODE PELAKSANAAN", "HASIL DAN PEMBAHASAN",
         "PENUTUP", "Gambaran Umum Masyarakat Sasaran", "Permasalahan",
         "Solusi Pemecahan Masalah", "Kontribusi Proyek bagi Masyarakat Sasaran",
         "Mitra yang Terlibat", "Penerapan IPTEKS",
         "Teknik Monitoring dan Evaluasi Proyek", "Simpulan", "Saran"],
        ["METODE PENELITIAN", "Landasan Teoretik" if False else "Teknik Analisis Data"],
    ),
    "proyek-proposal": (
        ["PENDAHULUAN", "KAJIAN PUSTAKA", "METODE PELAKSANAAN",
         "Teknik Monitoring dan Evaluasi Proyek"],
        ["HASIL DAN PEMBAHASAN", "PENUTUP"],
    ),
    "prototipe-laporan": (
        ["PENDAHULUAN", "KAJIAN PUSTAKA", "METODE PELAKSANAAN", "HASIL DAN PEMBAHASAN",
         "PENUTUP", "Rumusan Masalah", "Potensi Dampak Fungsional/Komersial",
         "Pendekatan Perancangan", "Prosedur Perancangan", "Teknik Perancangan",
         "Teknik Uji Kelayakan Hasil"],
        ["Subjek Penelitian/Sampel dan Populasi"],
    ),
    "prototipe-proposal": (
        ["PENDAHULUAN", "KAJIAN PUSTAKA", "METODE PELAKSANAAN", "Teknik Uji Kelayakan Hasil"],
        ["HASIL DAN PEMBAHASAN", "PENUTUP"],
    ),
    "publikasi-proposal": (
        ["PENDAHULUAN", "TINJAUAN PUSTAKA", "METODE", "Latar Belakang", "Rumusan Masalah",
         "Tujuan", "Manfaat", "Kebaruan"],
        ["METODE PENELITIAN", "METODE PELAKSANAAN", "NASKAH ARTIKEL ILMIAH"],
    ),
    "publikasi-laporan": (
        ["NASKAH ARTIKEL ILMIAH"],
        ["PENDAHULUAN", "TINJAUAN PUSTAKA", "METODE"],
    ),
    "publikasi-repositori": (
        ["TAUTAN DAN KETERANGAN PUBLIKASI", "Tautan Homepage Jurnal", "Keterangan Acceptance"],
        ["PENDAHULUAN", "NASKAH ARTIKEL ILMIAH"],
    ),
    "prestasi-laporan": (
        ["PENDAHULUAN", "LANDASAN TEORETIK", "METODE PELAKSANAAN KEGIATAN",
         "HASIL KEGIATAN DAN PEMBAHASAN", "Latar Belakang", "Tujuan Kegiatan",
         "Manfaat Kegiatan", "Strategi yang Dilakukan", "Waktu dan Tempat Kegiatan",
         "Sarana dan Prasarana Kegiatan"],
        ["KAJIAN PUSTAKA", "METODE PENELITIAN"],
    ),
    "prestasi-proposal": (
        ["PENDAHULUAN", "LANDASAN TEORETIK", "METODE PELAKSANAAN KEGIATAN"],
        [],
    ),
}

URUTAN_BAB = {
    "skripsi-laporan": 5, "proyek-laporan": 5, "prototipe-laporan": 5,
    "skripsi-proposal": 3, "proyek-proposal": 3, "prototipe-proposal": 3,
    "publikasi-proposal": 3, "publikasi-laporan": 1, "publikasi-repositori": 1,
    "prestasi-laporan": 4, "prestasi-proposal": 4, "skripsi-laporan-opsional": 5,
}


def teks(pdf: Path) -> str:
    hasil = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(pdf)],
                           capture_output=True, text=True, check=True)
    return hasil.stdout


def main() -> int:
    gagal = 0
    for nama, (harus, pantang) in HARAP.items():
        pdf = Path(f"{nama}.pdf")
        if not pdf.exists():
            print(f"[LEWAT] {nama}.pdf belum ada")
            gagal += 1
            continue
        isi = teks(pdf)
        masalah = []
        for kata in harus:
            if kata not in isi:
                masalah.append(f"tidak ada: '{kata}'")
        for kata in pantang:
            if kata in isi:
                masalah.append(f"seharusnya tidak ada: '{kata}'")
        nomor = [int(n) for n in re.findall(r"^BAB (\d+)\.$", isi, re.M)]
        if nomor != list(range(1, URUTAN_BAB[nama] + 1)):
            masalah.append(f"urutan bab {nomor}, diharapkan 1..{URUTAN_BAB[nama]}")
        if nama == "prestasi-proposal":
            log = Path(f"/tmp/sis-{nama}.log")
            if log.exists() and "tidak\nmemerlukan proposal" not in log.read_text(errors="ignore") \
                    and "memerlukan proposal" not in log.read_text(errors="ignore"):
                masalah.append("peringatan 'tidak memerlukan proposal' tidak muncul di log")
        status = "OK   " if not masalah else "GAGAL"
        print(f"[{status}] {nama}: bab 1..{URUTAN_BAB[nama]}"
              + ("" if not masalah else "\n         - " + "\n         - ".join(masalah)))
        gagal += bool(masalah)
    print(f"\n{len(HARAP) - gagal}/{len(HARAP)} varian sesuai sistematika panduan.")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
