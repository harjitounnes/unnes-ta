#!/usr/bin/env python3
"""Pemeriksa PDF template TA UNNES (todo t72).

Jalankan:  python3 skrip/qa.py [direktori ...]
Bawaan: seluruh direktori di contoh/. Opsi:
  --uji      ikut memeriksa PDF dokumen uji (uji/*.pdf, uji/sistematika, uji/sitasi)
  --ringkas  hanya mencetak baris ringkasan tiap dokumen

Semua angka diukur dari PDF dengan mutool, bukan dibaca dari berkas .tex:
  1. ukuran halaman A4 pada semua halaman;
  2. margin kiri 4 cm dan kanan 3 cm pada halaman isi (dilaporkan selisih terbesar);
  3. blok teks isi mulai pada margin atas 3 cm dan berhenti di batas bawah 3 cm; nomor halaman
     di kaki berada di dalam margin bawah (kebiasaan panduan halaman berjalan);
  4. huruf keluarga Times dan ukuran 12 pt pada teks isi;
  5. spasi antarbaris sesuai mode (panduan hal. 13: laporan 1,5; proposal 1,15; abstrak 1,0);
  6. nomor halaman: sampul tanpa nomor, bagian awal angka romawi kecil, bagian utama angka arab;
  7. nomor tabel/gambar mengikuti nomor bab tempatnya berada (panduan hal. 91);
  8. galat, overfull box, dan jumlah halaman.

Untuk penggalan di uji/ (bukan TA lengkap) hanya galat log dan ukuran halaman yang diperiksa.
"""
from __future__ import annotations

import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
A4 = (595.276, 841.89)
CM = 28.3465
KIRI, KANAN, ATAS, BAWAH = 4 * CM, 3 * CM, 3 * CM, 3 * CM
TOLERANSI = 2.0
TOLERANSI_BAWAH = 3.5      # bbox tinta descender dapat turun sedikit di bawah blok teks
UKURAN_HURUF = (11.8, 12.2)
KELUARGA_TIMES = ("NimbusRom", "Termes", "Times", "TeXGyre")
SPASI = {"laporan": 21.67, "proposal": 16.61, "abstrak": 14.45}
ROMAWI = re.compile(r"^[ivxlcdm]+$")
ANGKA = re.compile(r"^\d+$")


class Dokumen:
    """Akses halaman PDF: baris teks (posisi + isi) dan nomor halaman."""

    def __init__(self, pdf: Path):
        self.pdf = pdf
        self._stext: dict[int, ET.Element | None] = {}
        self._txt: dict[int, str] = {}
        info = subprocess.run(["mutool", "info", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s*(\d+)", info)
        self.halaman = int(m.group(1)) if m else 0

    def hlm(self, h: int) -> ET.Element | None:
        if h not in self._stext:
            keluaran = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(self.pdf), str(h)],
                                      capture_output=True, text=True).stdout
            try:
                self._stext[h] = ET.fromstring(keluaran).find("page")
            except ET.ParseError:
                self._stext[h] = None
        return self._stext[h]

    def teks(self, h: int) -> str:
        if h not in self._txt:
            self._txt[h] = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(self.pdf), str(h)],
                                          capture_output=True, text=True).stdout
        return self._txt[h]

    def tinggi(self, h: int) -> float:
        hlm = self.hlm(h)
        return float(hlm.get("height")) if hlm is not None else 0.0

    def baris(self, h: int) -> list[tuple[float, float, float, float, str]]:
        """Semua baris teks halaman: (y0, y1, x0, x1, teks), terurut dari atas."""
        hlm = self.hlm(h)
        if hlm is None:
            return []
        hasil = []
        for b in hlm.iter("line"):
            bbox = b.get("bbox")
            if not bbox:
                continue
            x0, y0, x1, y1 = (float(v) for v in bbox.split())
            teks = "".join(c.get("c", "") for c in b.iter("char"))
            hasil.append((y0, y1, x0, x1, teks))
        return sorted(hasil)

    def nomor_halaman(self, h: int) -> str | None:
        """Nomor halaman bila baris teks terbawah adalah angka di dalam margin bawah."""
        tinggi = self.tinggi(h)
        for y0, y1, x0, x1, teks in reversed(self.baris(h)):
            t = teks.strip()
            if not t:
                continue
            if y0 > tinggi - BAWAH - 2 and (ROMAWI.match(t) or ANGKA.match(t)):
                return t
            return None            # baris terbawah bukan nomor halaman
        return None

    def baris_isi(self, h: int) -> list[tuple[float, float, float, float, str]]:
        """Baris isi: baris berteks tanpa nomor halaman di kaki."""
        tinggi = self.tinggi(h)
        nomor = self.nomor_halaman(h)
        hasil = []
        for b in self.baris(h):
            if not b[4].strip():
                continue
            if nomor and b[4].strip() == nomor and b[0] > tinggi - BAWAH - 2:
                continue
            hasil.append(b)
        return hasil

    def halaman_bab_pertama(self) -> int | None:
        for h in range(1, self.halaman + 1):
            for b in self.baris(h):
                if re.fullmatch(r"BAB\s+1\.", b[4].strip()):
                    return h
        return None


def huruf_dominan(d: Dokumen, h: int):
    """(nama huruf, ukuran) dengan jumlah huruf terbanyak pada halaman."""
    hlm = d.hlm(h)
    if hlm is None:
        return None, None
    jumlah: dict[tuple[str, float], int] = {}
    for font in hlm.iter("font"):
        kunci = (font.get("name", "?"), round(float(font.get("size", 0)), 2))
        jumlah[kunci] = jumlah.get(kunci, 0) + sum(1 for _ in font.iter("char"))
    if not jumlah:
        return None, None
    return max(jumlah, key=lambda k: jumlah[k])


def periksa(direktori: Path):
    pdf = direktori / "main.pdf"
    if not pdf.exists():
        pdf = direktori.with_suffix(".pdf")
    if not pdf.exists():
        return [f"{direktori.name}: PDF tidak ditemukan"], {}
    log = pdf.with_suffix(".log")
    tex = pdf.with_suffix(".tex")
    masalah: list[str] = []
    ringkas: dict = {}

    log_teks = log.read_text(errors="ignore") if log.exists() else ""
    galat = re.findall(r"^! .*", log_teks, re.M)
    overfull = len(re.findall(r"^Overfull", log_teks, re.M))
    if galat:
        masalah.append(f"{len(galat)} galat pada log: {galat[0][:60]}")
    if overfull:
        masalah.append(f"{overfull} overfull box")

    isi_tex = tex.read_text(errors="ignore") if tex.exists() else ""
    mode = "proposal" if re.search(r"mode\s*=\s*\{?\s*proposal", isi_tex) else "laporan"
    # dokumen uji: penggalan, bukan TA lengkap, jadi tidak diperiksa bagian bagiannya
    fragmen = pdf.stem.startswith("uji") or "uji" in pdf.parts
    d = Dokumen(pdf)
    ringkas["halaman"] = d.halaman
    if d.halaman < 8 and not fragmen:
        masalah.append(f"hanya {d.halaman} halaman")

    bab = d.halaman_bab_pertama()
    isi_hal = [h for h in range(bab or 1, d.halaman + 1)]

    # Dokumen uji/penggalan (uji/*.pdf) bukan TA lengkap: hanya diperiksa galat log dan
    # ukuran halaman. Pemeriksaan tata letak lengkap dilakukan pada dokumen di contoh/.
    if fragmen:
        for h in range(1, d.halaman + 1):
            hlm = d.hlm(h)
            if hlm is None:
                masalah.append(f"halaman {h} tidak terbaca")
                continue
            lebar, tinggi = float(hlm.get("width")), float(hlm.get("height"))
            if abs(lebar - A4[0]) > 1 or abs(tinggi - A4[1]) > 1:
                masalah.append(f"halaman {h}: {lebar:.1f}x{tinggi:.1f} pt bukan A4")
        ringkas["fragmen"] = True
        return masalah, ringkas

    # ---- 1-3. ukuran halaman dan margin
    meleset = {"kiri": 0.0, "kanan": 0.0}
    atas_terukur = None
    for h in range(1, d.halaman + 1):
        hlm = d.hlm(h)
        if hlm is None:
            masalah.append(f"halaman {h} tidak terbaca")
            continue
        lebar, tinggi = float(hlm.get("width")), float(hlm.get("height"))
        if abs(lebar - A4[0]) > 1 or abs(tinggi - A4[1]) > 1:
            masalah.append(f"halaman {h}: {lebar:.1f}x{tinggi:.1f} pt bukan A4")
    # Batas kiri/kanan diukur dari seluruh halaman isi: halaman yang hanya memuat baris
    # terpusat (judul bab, daftar pustaka kosong) tidak boleh dianggap melanggar margin.
    semua_baris = [b for h in isi_hal for b in d.baris_isi(h)]
    kiri_global = min((b[2] for b in semua_baris), default=KIRI)
    kanan_global = max((b[3] for b in semua_baris), default=A4[0] - KANAN)
    meleset["kiri"] = abs(kiri_global - KIRI)
    meleset["kanan"] = abs((A4[0] - KANAN) - kanan_global)
    if meleset["kiri"] > TOLERANSI:
        masalah.append(f"batas kiri teks isi {kiri_global:.1f} pt, seharusnya {KIRI:.1f} pt")
    if meleset["kanan"] > TOLERANSI:
        masalah.append(f"batas kanan teks isi {kanan_global:.1f} pt, seharusnya {A4[0] - KANAN:.1f} pt")
    for h in isi_hal:
        baris = d.baris_isi(h)
        if not baris:
            continue
        for y0_, y1_, x0_, x1_, t_ in baris:
            if x1_ > A4[0] - KANAN + TOLERANSI:
                masalah.append(f"halaman {h}: '{t_.strip()[:30]}' melewati margin kanan "
                               f"{x1_ - (A4[0] - KANAN):+.1f} pt")
                break
            if x0_ < KIRI - TOLERANSI:
                masalah.append(f"halaman {h}: '{t_.strip()[:30]}' melewati margin kiri "
                               f"{KIRI - x0_:+.1f} pt")
                break
        y0 = min(b[0] for b in baris)
        # halaman yang mulai dari batas atas blok teks (bukan halaman judul bab/gambar)
        if y0 - ATAS < 6:
            atas_terukur = y0 - ATAS if atas_terukur is None else min(atas_terukur, y0 - ATAS)
        bawah = max(b[1] for b in baris) - (A4[1] - BAWAH)
        if bawah > TOLERANSI_BAWAH:
            masalah.append(f"halaman {h}: teks isi melewati batas bawah {bawah:+.1f} pt")
    ringkas["meleset"] = meleset
    ringkas["atas"] = atas_terukur
    if atas_terukur is None:
        masalah.append("tidak ada halaman yang mulai dari batas atas blok teks")
    elif not -TOLERANSI <= atas_terukur <= 8:
        masalah.append(f"jarak tepi atas ke huruf pertama {atas_terukur:.1f} pt (margin atas 3 cm)")

    # ---- 4. huruf
    tebal = max(isi_hal, key=lambda h: len(d.baris_isi(h))) if isi_hal else 1
    huruf, ukuran = huruf_dominan(d, tebal)
    if huruf:
        ringkas["huruf"] = f"{huruf} {ukuran:.2f}"
        if not any(k in huruf for k in KELUARGA_TIMES):
            masalah.append(f"huruf teks isi {huruf}, bukan keluarga Times")
        if not UKURAN_HURUF[0] <= ukuran <= UKURAN_HURUF[1]:
            masalah.append(f"ukuran huruf isi {ukuran:.2f} pt, bukan 12 pt")
    else:
        masalah.append("huruf tidak terbaca")

    # ---- 5. spasi antarbaris
    def baris_prosa(h: int):
        """Baris prosa penuh: mulai di margin kiri dan berakhir di margin kanan."""
        return [b for b in d.baris_isi(h)
                if abs((A4[0] - KANAN) - b[3]) <= 2 and abs(b[2] - KIRI) <= 2]

    def gap_prosa(h: int) -> list[float]:
        """Jarak dari baris prosa penuh ke baris berikutnya: ukuran spasi antarbaris."""
        baris = d.baris_isi(h)
        return [b[0] - a[0] for a, b in zip(baris, baris[1:])
                if abs((A4[0] - KANAN) - a[3]) <= 2 and abs(a[2] - KIRI) <= 2 and 8 < b[0] - a[0] < 40]

    semua_gap = [g for h in isi_hal for g in gap_prosa(h)]
    catatan: list[str] = []
    if semua_gap:
        spasi = statistics.mode([round(g, 1) for g in semua_gap])
        ringkas["spasi"] = round(spasi, 2)
        ringkas["baris-prosa"] = len(semua_gap)
        if abs(spasi - SPASI[mode]) > 1.0:
            masalah.append(f"spasi {mode} {spasi:.2f} pt, diharapkan {SPASI[mode]:.2f} pt")
    else:
        catatan.append("tidak ada baris prosa pada bagian utama (mode repositori: hanya tautan)")
    ringkas["catatan"] = catatan

    for h in range(1, bab or d.halaman):          # abstrak wajib berspasi tunggal
        teks = d.teks(h)
        if "ABSTRAK" in teks and "Kata kunci" in teks:
            gap = gap_prosa(h)
            s = statistics.mode([round(g, 1) for g in gap]) if gap else None
            if s:
                ringkas["spasi-abstrak"] = round(s, 2)
                if abs(s - SPASI["abstrak"]) > 1.0:
                    masalah.append(f"spasi abstrak {s:.2f} pt, diharapkan {SPASI['abstrak']:.2f} pt")
            break

    # ---- 6. nomor halaman (dokumen uji/penggalan tidak diperiksa bagiannya)
    if fragmen:
        return masalah, ringkas
    if d.nomor_halaman(1):
        masalah.append(f"sampul memuat nomor halaman '{d.nomor_halaman(1)}'")
    if bab:
        romawi = [n for n in (d.nomor_halaman(h) for h in range(2, bab)) if n]
        if not romawi:
            masalah.append("bagian awal tidak memuat nomor halaman")
        elif not all(ROMAWI.match(n) for n in romawi):
            masalah.append(f"nomor bagian awal bukan romawi: {romawi[:4]}")
        ringkas["romawi"] = f"{romawi[0]}..{romawi[-1]}" if romawi else "-"
        arab = [n for n in (d.nomor_halaman(h) for h in range(bab, min(bab + 4, d.halaman + 1))) if n]
        if not arab or not all(ANGKA.match(n) for n in arab):
            masalah.append(f"nomor bagian utama bukan angka arab: {arab}")
    else:
        masalah.append("penanda 'BAB 1.' tidak ditemukan")

    # ---- 7. penomoran tabel/gambar menurut bab
    bab_kini = 0
    keluaran = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(d.pdf)],
                              capture_output=True, text=True).stdout
    for baris in keluaran.splitlines():
        m = re.match(r"^BAB (\d+)\.$", baris.strip())
        if m:
            bab_kini = int(m.group(1))
            continue
        m = re.match(r"^(?:Tabel|Gambar) (\d+)\.(\d+)", baris.strip())
        if m and bab_kini and int(m.group(1)) != bab_kini:
            masalah.append(f"'{baris.strip()[:40]}' berada di BAB {bab_kini}")

    return masalah, ringkas


def kumpulkan(argv: list[str]) -> list[Path]:
    argumen = [a for a in argv[1:] if not a.startswith("--")]
    if argumen:
        return [Path(a) for a in argumen]
    # hanya direktori yang benar-benar memuat dokumen (contoh/data/ bukan dokumen)
    daftar = sorted(d for d in (AKAR / "contoh").iterdir()
                    if d.is_dir() and ((d / "main.pdf").exists() or (d / "main.tex").exists()))
    if "--uji" in argv:
        daftar += sorted((AKAR / "uji").glob("*.pdf"))
        daftar += sorted((AKAR / "uji" / "sistematika").glob("*.pdf"))
        daftar += sorted((AKAR / "uji" / "sitasi").glob("*.pdf"))
    return daftar


def main(argv: list[str]) -> int:
    daftar = kumpulkan(argv)
    gagal = 0
    for d in daftar:
        masalah, r = periksa(d)
        m = r.get("meleset", {})
        ringkas = " | ".join([
            f"{r.get('halaman', 0):3d} hlm",
            (f"spasi isi {r['spasi']:5.2f} pt (n={r.get('baris-prosa', 0)})"
             if "spasi" in r else "spasi isi    ?    ") + (f" abstrak {r['spasi-abstrak']:.2f}"
                                                    if "spasi-abstrak" in r else ""),
            (f"atas {r['atas']:4.1f} pt" if r.get("atas") is not None else "atas   ?    "),
            f"meleset kiri {m.get('kiri', 0):4.1f} kanan {m.get('kanan', 0):4.1f} pt",
            f"{r.get('huruf', '-')}",
            f"nomor {r.get('romawi', '-')}/arab",
        ])
        status = "OK   " if not masalah else "GAGAL"
        print(f"[{status}] {d.name:22s} {ringkas}")
        if "--ringkas" not in argv:
            for x in masalah:
                print(f"         - {x}")
            for c in r.get("catatan", []):
                print(f"         ~ {c}")
        gagal += bool(masalah)
    print(f"\n{len(daftar) - gagal}/{len(daftar)} dokumen lolos pemeriksaan QA.")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
