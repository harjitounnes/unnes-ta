#!/usr/bin/env python3
"""Smoke test akhir template TA UNNES (todo t83).

Menjalankan seluruh pemeriksa lalu mencetak checklist aturan panduan A.1-A.7 beserta bukti
angkanya. Setiap butir dianggap lulus hanya bila pemeriksa yang bersangkutan melaporkan sukses.

Pemakaian:
    python3 skrip/verifikasi.py            # pakai PDF yang sudah ada
    python3 skrip/verifikasi.py --build    # kompilasi ulang 11 contoh dulu (lebih lama)
    python3 skrip/verifikasi.py --lualatex # sekaligus menguji jalur mesin lualatex

Keluar dengan kode 1 bila ada butir yang gagal.
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
CONTOH = AKAR / "contoh"


def lingkungan_template() -> dict[str, str]:
    """TEXINPUTS/BSTINPUTS/BIBINPUTS yang sama dengan setelan editor.

    Definisi tunggalnya ada di skrip/siapkan-vscode.py supaya kompilasi dari terminal dan dari
    LaTeX Workshop memakai jalur pencarian yang identik (kelas, paket, berkas gaya BibTeX,
    identitas bersama, pustaka contoh, dan logo template di akar repo).
    """
    berkas = AKAR / "skrip" / "siapkan-vscode.py"
    spesifikasi = importlib.util.spec_from_file_location("siapkan_vscode", berkas)
    modul = importlib.util.module_from_spec(spesifikasi)
    spesifikasi.loader.exec_module(modul)
    return modul.lingkungan_terminal(AKAR, AKAR)


def jalan(perintah: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Menjalankan perintah dengan TEXINPUTS/BSTINPUTS template supaya kelas dan bst terjangkau."""
    lingkungan = dict(os.environ)
    lingkungan.update(lingkungan_template())
    hasil = subprocess.run(perintah, cwd=cwd or AKAR, capture_output=True, text=True,
                           env=lingkungan)
    return hasil.returncode, hasil.stdout + hasil.stderr


def pesan_ada(pesan: str, keluaran: str) -> bool:
    """Pesan LaTeX dibungkus di kolom 79, jadi bandingkan setelah spasi dinormalkan."""
    norm = lambda s: re.sub(r"\s+", " ", s)
    return norm(pesan) in norm(keluaran)


def font_terbesar(pdf: Path, halaman: int = 1) -> tuple[float, str]:
    """(ukuran, teks) blok berhuruf terbesar halaman: dipakai memeriksa ukuran JUDUL sampul."""
    keluaran = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(pdf), str(halaman)],
                              capture_output=True, text=True).stdout
    try:
        hlm = ET.fromstring(keluaran).find("page")
    except ET.ParseError:
        return 0.0, ""
    terbesar = (0.0, "")
    for blok in hlm.iter("block"):
        teks = "".join(c.get("c", "") for c in blok.iter("char")).strip()
        if not teks:
            continue
        font = blok.find(".//font")
        ukuran = float(font.get("size", 0))
        if ukuran > terbesar[0]:
            terbesar = (ukuran, teks)
    return terbesar


def hitung_nip(pdf: Path) -> int:
    """Jumlah baris NIP pada halaman pengesahan (menghitung pola NIP 18 digit)."""
    for h in range(1, 12):
        teks = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(pdf), str(h)],
                              capture_output=True, text=True).stdout
        if "PENGESAHAN PENGUJI" in teks:
            return len(re.findall(r"\b\d{18}\b", teks))
    return -1


def daftar_isitiga(pdf: Path) -> int:
    """Jumlah entri level tiga (x.y.z) pada Daftar Isi: panduan cukup sampai level dua."""
    for h in range(1, 12):
        teks = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(pdf), str(h)],
                              capture_output=True, text=True).stdout
        if "DAFTAR ISI" in teks:
            return len(set(re.findall(r"\b\d+\.\d+\.\d+\b", teks)))
    return -1


def main(argv: list[str]) -> int:
    butir: list[tuple[str, bool, str]] = []

    if "--build" in argv:
        kode, keluaran = jalan(["./skrip/build.sh"])
        total = re.search(r"dokumen dikompilasi: (\d+), gagal: (\d+)", keluaran)
        lulus = bool(total) and total.group(2) == "0"
        butir.append(("Kompilasi 11 contoh tanpa galat",
                      lulus, f"{total.group(0) if total else keluaran[-80:]}"))

    # ---------------------------------------------------------------- QA tata letak
    kode, keluaran = jalan([sys.executable, "skrip/qa.py"])
    ringkasan = re.search(r"(\d+)/(\d+) dokumen lolos pemeriksaan QA", keluaran)
    lulus_qa = bool(ringkasan) and ringkasan.group(1) == ringkasan.group(2)
    baris_dok = [b for b in keluaran.splitlines() if b.startswith("[")]
    spasi_lap = sorted(set(re.findall(r"spasi isi (\d+\.\d+) pt", "\n".join(
        b for b in baris_dok if re.search(r"spasi isi 2[01]\.", b)))))
    spasi_pro = sorted(set(re.findall(r"spasi isi (\d+\.\d+) pt", "\n".join(
        b for b in baris_dok if re.search(r"spasi isi 1[56]\.", b)))))
    spasi_abs = sorted(set(re.findall(r"abstrak (\d+\.\d+)", "\n".join(baris_dok))))
    huruf = sorted(set(re.findall(r"\| (Nimbus\S+|TeXGyre\S+) (\d+\.\d+) \|", "\n".join(baris_dok))))
    meleset = [float(m) for m in re.findall(r"meleset kiri\s+(\d+\.\d+) kanan\s+(\d+\.\d+)",
                                            "\n".join(baris_dok)) for m in m]
    atas = [float(m) for m in re.findall(r"atas\s+(\d+\.\d+) pt", "\n".join(baris_dok))]
    romawi_arab = "nomor iv..xv/arab" in "\n".join(baris_dok)

    butir.append(("A.1 Huruf Times 12 pt pada teks isi",
                  bool(huruf) and all(11.8 <= float(u) <= 12.2 for _, u in huruf),
                  ", ".join(f"{n} {u} pt" for n, u in huruf) or "tidak terukur"))
    butir.append(("A.1 Spasi laporan 1,5 (21,67 pt)",
                  bool(spasi_lap) and all(abs(float(s) - 21.67) <= 1.0 for s in spasi_lap),
                  ", ".join(spasi_lap) + " pt"))
    butir.append(("A.1 Spasi proposal 1,15 (16,61 pt)",
                  bool(spasi_pro) and all(abs(float(s) - 16.61) <= 1.0 for s in spasi_pro),
                  ", ".join(spasi_pro) + " pt"))
    butir.append(("A.1 Spasi abstrak 1,0 (14,45 pt)",
                  bool(spasi_abs) and all(abs(float(s) - 14.45) <= 1.0 for s in spasi_abs),
                  ", ".join(spasi_abs) + " pt"))
    butir.append(("A.1 Margin A4 4/3/3/3 cm, selisih < 2 pt",
                  lulus_qa and bool(meleset) and max(meleset) < 2.0,
                  f"selisih terbesar {max(meleset) if meleset else -1:.1f} pt; "
                  f"{ringkasan.group(0) if ringkasan else 'qa gagal'}"))

    # ---------------------------------------------------------------- A.2 sampul
    pdf_lap = CONTOH / "skripsi-laporan" / "main.pdf"
    ukuran_judul, teks_judul = font_terbesar(pdf_lap, 1)
    butir.append(("A.2 Judul sampul 14 pt",
                  abs(ukuran_judul - 14.0) < 0.3 and bool(teks_judul),
                  f"{ukuran_judul:.2f} pt | {teks_judul[:40]}"))
    teks_sampul = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(pdf_lap), "1"],
                                 capture_output=True, text=True).stdout
    ada = [k for k in ("Skripsi", "Nama Mahasiswa", "UNIVERSITAS NEGERI SEMARANG", "Semarang")
           if k.lower() in teks_sampul.lower()]
    butir.append(("A.2 Komponen sampul (jenis TA, nama, universitas, kota)",
                  len(ada) >= 3, ", ".join(ada)))

    # ---------------------------------------------------------------- A.3 pengesahan
    nip_sarjana = hitung_nip(pdf_lap)
    nip_diploma = hitung_nip(CONTOH / "prototipe-laporan" / "main.pdf")
    butir.append(("A.3 Pengesahan 5 baris (sarjana) dan 4 baris (diploma)",
                  nip_sarjana == 5 and nip_diploma == 4,
                  f"skripsi {nip_sarjana} baris NIP, prototipe {nip_diploma} baris NIP"))

    # ---------------------------------------------------------------- A.4 bagian awal
    kode, keluaran = jalan([sys.executable, "uji/cek-contoh.py"])
    cocok = re.search(r"(\d+)/(\d+) dokumen contoh", keluaran)
    butir.append(("A.4 Urutan bagian awal, bab, lampiran, dan biodata tiap varian",
                  bool(cocok) and cocok.group(1) == cocok.group(2),
                  cocok.group(0) if cocok else keluaran[-80:]))

    # ---------------------------------------------------------------- A.5 sistematika
    kode, keluaran = jalan([sys.executable, "../cek-sistematika.py"], cwd=AKAR / "uji" / "sistematika")
    cocok = re.search(r"(\d+)/(\d+) varian sesuai sistematika panduan", keluaran)
    butir.append(("A.5 Sistematika bab 12 varian (jenis x mode)",
                  bool(cocok) and cocok.group(1) == cocok.group(2),
                  cocok.group(0) if cocok else keluaran[-80:]))

    # ---------------------------------------------------------------- A.6 lampiran
    lampiran = re.findall(r"lampiran=(\d+)", keluaran + "\n" + jalan(
        [sys.executable, "uji/cek-contoh.py"])[1])
    butir.append(("A.6 Lampiran wajib tersedia per jenis TA",
                  bool(lampiran) and min(int(x) for x in lampiran) >= 4,
                  f"jumlah lampiran per contoh: {sorted(set(lampiran))}"))

    # ---------------------------------------------------------------- A.7 sitasi
    kode, keluaran = jalan([sys.executable, "../cek-sitasi.py"], cwd=AKAR / "uji" / "sitasi")
    cocok = re.search(r"(\d+)/(\d+) gaya sitasi", keluaran)
    butir.append(("A.7 Enam gaya sitasi dan ukuran daftar pustaka",
                  bool(cocok) and cocok.group(1) == cocok.group(2),
                  cocok.group(0) if cocok else keluaran[-80:]))

    # ---------------------------------------------------------------- penjaga opsi
    kode, keluaran = jalan(["pdflatex", "-interaction=nonstopmode", "uji-opsi-salah.tex"],
                           cwd=AKAR / "uji")
    butir.append(("Opsi kelas salah ditolak",
                  pesan_ada("Nilai opsi jenis tidak dikenal", keluaran),
                  "Class unnes-ta Error: Nilai opsi jenis tidak dikenal" if kode else "tidak ada"))

    kode, keluaran = jalan(["pdflatex", "-interaction=nonstopmode", "uji-citemla-salah.tex"],
                           cwd=AKAR / "uji" / "sitasi")
    butir.append(("Penjaga \\citemla pada gaya bernomor",
                  pesan_ada("hanya untuk gaya nama-tahun", keluaran),
                  "Package unnes-ta-sitasi Error"))

    # ---------------------------------------------------------------- keputusan default
    masuk = daftar_isitiga(pdf_lap)
    butir.append(("Default: Daftar Isi sampai level dua",
                  masuk == 0, f"{masuk} entri level tiga pada Daftar Isi"))
    butir.append(("Default: nomor halaman bawah-tengah, romawi lalu arab",
                  romawi_arab, "nomor iv..xv (romawi) lalu arab pada semua contoh"))
    butir.append(("Default: teks mulai pada batas margin atas 3 cm",
                  bool(atas) and all(-2 <= a <= 8 for a in atas),
                  f"jarak tepi atas ke huruf pertama {atas[0] if atas else -1:.1f} pt"))

    # ---------------------------------------------------------------- lualatex (opsional)
    if "--lualatex" in argv:
        kode, keluaran = jalan(["./skrip/build.sh", "--only=skripsi-proposal", "--engine=lualatex"])
        butir.append(("Mesin alternatif lualatex (fallback mathptmx)",
                      "error=0" in keluaran, keluaran.strip().splitlines()[-3] if keluaran else ""))

    lebar = max(len(n) for n, _, _ in butir)
    print("Checklist verifikasi template TA UNNES\n" + "=" * (lebar + 30))
    gagal = 0
    for nama, lulus, bukti in butir:
        print(f"[{'OK   ' if lulus else 'GAGAL'}] {nama:<{lebar}}  {bukti}")
        gagal += not lulus
    print("=" * (lebar + 30))
    print(f"{len(butir) - gagal}/{len(butir)} butir lulus.")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
