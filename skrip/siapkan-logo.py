#!/usr/bin/env python3
"""Menyiapkan berkas logo template dari logo sumber milik repo.

Sumber bawaan: `Logo-Transparan-Warna-1.png` di akar repo — logo UNNES berwarna dengan latar
transparan (lambang + tulisan "UNNES" + tulisan "UNIVERSITAS NEGERI SEMARANG"). Berkas itu
disalin apa adanya menjadi `logo/logo-unnes-warna.png`, lalu dibuat versi **hitam putih**:

  logo/logo-unnes.png   versi hitam putih berlatarkan transparan (dipakai sampul secara bawaan)
                        Warna tinta logo (emas, merah, biru) menjadi hitam; bagian putih logo
                        tetap putih; latar transparan tetap transparan.

Cara pakai:
  python3 skrip/siapkan-logo.py [berkas-logo.png] [--faktor=3]

`--faktor` menyusutkan gambar dengan rata-rata kotak (bawaan 3) supaya berkas hasil tidak
berlebihan dan tepinya tetap halus saat dicetak. Logo sumber 1528 x 2037 piksel menjadi
509 x 679 piksel (setara ~430 dpi untuk tinggi cetak 3 cm).
"""

import pathlib
import shutil
import struct
import sys
import zlib

AKAR = pathlib.Path(__file__).resolve().parent.parent
# Berkas sumber: logo di akar repo; bila dihapus, dipakai salinan di logo/logo-unnes-warna.png
SUMBER_BAWAAN = [AKAR / "Logo-Transparan-Warna-1.png", AKAR / "logo" / "logo-unnes-warna.png"]
TUJUAN_HITAM = AKAR / "logo" / "logo-unnes.png"
TUJUAN_WARNA = AKAR / "logo" / "logo-unnes-warna.png"

AMBANG_TINTA = 40          # jarak minimum dari putih agar piksel dianggap tinta hitam
AMBANG_PUTIH = 12          # jarak maksimum dari putih agar piksel dianggap putih (bukan tinta)


# ------------------------------------------------------------------- baca PNG
def baca_png(berkas: pathlib.Path):
    """Mengembalikan (lebar, tinggi, piksel RGBA). Mendukung palet (tipe 3) dan RGBA (tipe 6)."""
    data = berkas.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"bukan berkas PNG: {berkas}")
    pos, idat, palet, trns, ihdr = 8, b"", None, None, None
    while pos < len(data):
        panjang, jenis = struct.unpack(">I4s", data[pos:pos + 8])
        isi = data[pos + 8:pos + 8 + panjang]
        if jenis == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", isi)
        elif jenis == b"PLTE":
            palet = isi
        elif jenis == b"tRNS":
            trns = isi
        elif jenis == b"IDAT":
            idat += isi
        elif jenis == b"IEND":
            break
        pos += 12 + panjang

    lebar, tinggi, kedalaman, tipe, _, _, antar = ihdr
    if antar:
        raise SystemExit("PNG terinterlasi belum didukung")
    if tipe not in (3, 6):
        raise SystemExit(f"tipe warna PNG {tipe} belum didukung (pakai palet 3 atau RGBA 6)")

    saluran = 4 if tipe == 6 else 1
    bit_per_piksel = 32 if tipe == 6 else kedalaman
    lebar_baris = (lebar * bit_per_piksel + 7) // 8
    mentah = zlib.decompress(idat)
    sebelum = bytearray(lebar_baris)
    baris_piksel, pos = [], 0
    for _ in range(tinggi):
        jenis_filter = mentah[pos]
        pos += 1
        baris = bytearray(mentah[pos:pos + lebar_baris])
        pos += lebar_baris
        for i in range(lebar_baris):
            kiri = baris[i - saluran] if i >= saluran else 0
            atas = sebelum[i]
            kiri_atas = sebelum[i - saluran] if i >= saluran else 0
            if jenis_filter == 1:
                baris[i] = (baris[i] + kiri) & 0xFF
            elif jenis_filter == 2:
                baris[i] = (baris[i] + atas) & 0xFF
            elif jenis_filter == 3:
                baris[i] = (baris[i] + (kiri + atas) // 2) & 0xFF
            elif jenis_filter == 4:
                p = kiri + atas - kiri_atas
                pa, pb, pc = abs(p - kiri), abs(p - atas), abs(p - kiri_atas)
                acuan = kiri if (pa <= pb and pa <= pc) else (atas if pb <= pc else kiri_atas)
                baris[i] = (baris[i] + acuan) & 0xFF
        baris_piksel.append(bytes(baris))
        sebelum = baris

    rgba = bytearray()
    if tipe == 6:
        rgba += b"".join(baris_piksel)
    else:                                     # palet 1/2/4/8 bit
        daftar = [tuple(palet[i * 3:i * 3 + 3]) for i in range(len(palet) // 3)]
        alpha_palet = list(trns) if trns else [255] * len(daftar)
        per_piksel = 8 // kedalaman
        topeng = (1 << kedalaman) - 1
        for baris in baris_piksel:
            for i in range(lebar):
                bit = i * kedalaman
                nilai = (baris[bit // 8] >> (8 - kedalaman - (bit % 8))) & topeng
                warna = daftar[nilai]
                alpha = alpha_palet[nilai] if nilai < len(alpha_palet) else 255
                rgba += bytes(warna) + bytes((alpha,))
    return lebar, tinggi, bytes(rgba)


# ------------------------------------------------------- hitam putih + penyusutan
def jadi_hitam_putih(lebar: int, tinggi: int, rgba: bytes) -> bytes:
    """Mengubah tinta berwarna menjadi hitam; putih tetap putih; transparan tetap transparan."""
    keluar = bytearray(len(rgba))
    for i in range(0, len(rgba), 4):
        r, g, b, a = rgba[i], rgba[i + 1], rgba[i + 2], rgba[i + 3]
        tinta = max(255 - r, 255 - g, 255 - b)          # jarak dari putih
        if a == 0 or tinta <= AMBANG_PUTIH:             # latar/putih logo
            keluar[i:i + 4] = bytes((255, 255, 255, a))
        else:
            keluar[i:i + 4] = bytes((0, 0, 0, a))
    return bytes(keluar)


def susutkan(lebar: int, tinggi: int, rgba: bytes, faktor: int):
    """Menyusutkan gambar dengan rata-rata kotak faktor x faktor (warna dibobot alpha)."""
    if faktor < 2:
        return lebar, tinggi, rgba
    keluar_lebar, keluar_tinggi = lebar // faktor, tinggi // faktor
    keluar = bytearray(keluar_lebar * keluar_tinggi * 4)
    for y in range(keluar_tinggi):
        for x in range(keluar_lebar):
            jr = jg = jb = ja = 0
            for dy in range(faktor):
                dasar = ((y * faktor + dy) * lebar + x * faktor) * 4
                for dx in range(faktor):
                    i = dasar + dx * 4
                    a = rgba[i + 3]
                    jr += rgba[i] * a
                    jg += rgba[i + 1] * a
                    jb += rgba[i + 2] * a
                    ja += a
            jumlah = faktor * faktor
            tujuan = (y * keluar_lebar + x) * 4
            if ja:
                keluar[tujuan] = jr // ja
                keluar[tujuan + 1] = jg // ja
                keluar[tujuan + 2] = jb // ja
            else:
                keluar[tujuan] = keluar[tujuan + 1] = keluar[tujuan + 2] = 255
            keluar[tujuan + 3] = ja // jumlah
    return keluar_lebar, keluar_tinggi, bytes(keluar)


def pangkas_transparan(lebar: int, tinggi: int, rgba: bytes, ambang: int = 8):
    """Memangkas tepi yang (hampir) transparan supaya logo mengisi kotaknya di sampul."""
    baris_isi = [any(rgba[(y * lebar + x) * 4 + 3] > ambang for x in range(lebar))
                 for y in range(tinggi)]
    atas = next(y for y, isi in enumerate(baris_isi) if isi)
    bawah = max(y for y, isi in enumerate(baris_isi) if isi)
    kiri, kanan = lebar, -1
    for y in range(atas, bawah + 1):
        for x in range(lebar):
            if rgba[(y * lebar + x) * 4 + 3] > ambang:
                kiri, kanan = min(kiri, x), max(kanan, x)
    potong = bytearray()
    for y in range(atas, bawah + 1):
        potong += rgba[(y * lebar + kiri) * 4:(y * lebar + kanan + 1) * 4]
    return kanan - kiri + 1, bawah - atas + 1, bytes(potong)


# ------------------------------------------------------------------- tulis PNG
def tulis_png(berkas: pathlib.Path, lebar: int, tinggi: int, rgba: bytes) -> None:
    """Menulis PNG RGBA 8 bit (filter 0) dengan kompresi maksimum."""
    def potongan(jenis: bytes, isi: bytes) -> bytes:
        return (struct.pack(">I", len(isi)) + jenis + isi
                + struct.pack(">I", zlib.crc32(jenis + isi) & 0xFFFFFFFF))

    mentah = bytearray()
    for y in range(tinggi):
        mentah.append(0)
        mentah += rgba[y * lebar * 4:(y + 1) * lebar * 4]
    berkas.write_bytes(b"\x89PNG\r\n\x1a\n"
                       + potongan(b"IHDR", struct.pack(">IIBBBBB", lebar, tinggi, 8, 6, 0, 0, 0))
                       + potongan(b"IDAT", zlib.compress(bytes(mentah), 9))
                       + potongan(b"IEND", b""))


# ----------------------------------------------------------------------- utama
def main() -> int:
    argumen = [a for a in sys.argv[1:] if not a.startswith("--")]
    faktor = 3
    for a in sys.argv[1:]:
        if a.startswith("--faktor="):
            faktor = int(a.split("=", 1)[1])
    if argumen:
        sumber = pathlib.Path(argumen[0])
    else:
        sumber = next((s for s in SUMBER_BAWAAN if s.exists()), SUMBER_BAWAAN[0])
    if not sumber.exists():
        raise SystemExit(f"berkas logo sumber tidak ada: {sumber}")

    TUJUAN_HITAM.parent.mkdir(parents=True, exist_ok=True)
    if sumber.resolve() != TUJUAN_WARNA.resolve():
        shutil.copyfile(sumber, TUJUAN_WARNA)             # versi warna apa adanya (hemat ukuran)

    lebar, tinggi, rgba = baca_png(sumber)
    lebar, tinggi, rgba = pangkas_transparan(lebar, tinggi, rgba)
    lebar_kecil, tinggi_kecil, rgba_kecil = susutkan(lebar, tinggi, jadi_hitam_putih(lebar, tinggi, rgba),
                                                     faktor)
    tulis_png(TUJUAN_HITAM, lebar_kecil, tinggi_kecil, rgba_kecil)

    print(f"sumber        : {sumber.name} — {lebar}x{tinggi} piksel setelah tepi transparan dipangkas")
    print(f"{TUJUAN_WARNA.relative_to(AKAR)} : versi warna asli (salinan, {(TUJUAN_WARNA.stat().st_size + 512) // 1024} KB)")
    print(f"{TUJUAN_HITAM.relative_to(AKAR)}         : hitam putih, latar transparan, "
          f"{lebar_kecil}x{tinggi_kecil} piksel ({(TUJUAN_HITAM.stat().st_size + 512) // 1024} KB), "
          f"penyusutan 1/{faktor}")
    print(f"proporsi      : lebar/tinggi = 1 : {tinggi_kecil / lebar_kecil:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
