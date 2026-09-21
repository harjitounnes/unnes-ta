#!/usr/bin/env python3
"""Menulis .vscode/settings.json LaTeX Workshop di setiap folder dokumen.

Masalah yang dipecahkan: kelas unnes-ta.cls, paket unnes-ta-*.sty, berkas gaya
bst/unnes-apalike-apa.bst, pustaka referensi/contoh.bib, dan gambar/logo template semuanya ada di
akar repo, sedangkan main.tex disunting dan dikompilasi dari dalam folder dokumen
(<proyek>/<dokumen>/, mis. contoh/skripsi-laporan atau proyek_satu/skripsi-laporan). Tanpa
TEXINPUTS/BSTINPUTS/BIBINPUTS, pdflatex berhenti dengan galat seperti "File `unnes-ta.cls' not
found", dan berkas gaya BibTeX tidak ditemukan oleh bibtex.

Skrip ini menuliskan setelan LaTeX Workshop yang menyuntikkan variabel lingkungan tersebut ke
setiap pemanggilan pdflatex/bibtex. Setelah itu cukup menekan Ctrl+S di code-server/VS Code:
dokumen langsung dikompilasi ulang (pdflatex -> bibtex -> pdflatex -> pdflatex) tanpa perlu
mengetik ekspor variabel apa pun, dan tanpa peduli seberapa dalam folder dokumen berada.

Setelan itu TIDAK memuat jalur absolut PC tempat skrip ini dijalankan, sehingga repo boleh
dipindahkan ke PC lain (nama pengguna, letak home, dan nama direktori repo boleh berbeda) tanpa
menyunting apa pun:

    %DIR%            placeholder LaTeX Workshop, diisi direktori berkas utama saat resep berjalan
                     (replaceArgumentPlaceholders di ekstensi); berlaku untuk argumen maupun env
    %DIR%/../..      direktori induk folder dokumen (tingkat 1, 2, ... sampai akar repo)
    $TEXMFDIST/...   dikembangkan kpathsea (pdflatex, bibtex) dari texmf.cnf mesin yang dipakai,
                     jadi letak TeX Live tidak perlu diketahui saat skrip ini dijalankan

Karena %DIR% diisi saat kompilasi, setelan yang sama tetap benar baik yang dibuka code-server/VS
Code adalah folder dokumen itu sendiri maupun akar repo — jalur relatif ../.. pada main.tex pun
tidak lagi menentukan.

Urutan pencarian sengaja dimulai dari berkas di direktori dokumen (":" pertama), lalu direktori
induk terdekat, sehingga data milik dokumen selalu menang: identitas.tex, pustaka .bib, atau kelas
lokal di folder itu dipakai lebih dahulu, baru berkas template di akar repo.

Satu-satunya perkecualian: folder dokumen yang berada DI LUAR akar repo (mis. hasil
skrip/salin-dokumen.py ke ~/tugas-akhir-saya) tidak bisa dijangkau %DIR% dengan cara apa pun,
sehingga jalur absolut akar repo saat ini yang dipakai dan skrip ini harus dijalankan ulang di PC
tempat repo template berada.

Pemakaian:
    python3 skrip/siapkan-vscode.py                      # akar repo + semua folder dokumen
    python3 skrip/siapkan-vscode.py <folder> [<folder>…] # hanya folder yang disebut
    python3 skrip/siapkan-vscode.py --akar=/path/lain <folder>
"""
from __future__ import annotations

import argparse
import json
import pathlib

# Placeholder LaTeX Workshop yang diisi saat resep dijalankan. Seluruh jalur di bawah dibangun dari
# placeholder ini supaya tidak ada jalur PC tertentu yang tertulis di berkas setelan.
DIR_UTAMA = "%DIR%"

# Direktori berkas gaya BibTeX bawaan TeX Live. Ditulis sebagai variabel kpathsea, bukan jalur
# hasil kpsewhich saat skrip dijalankan: pdflatex/bibtex mengembangkan $TEXMFDIST sendiri dari
# texmf.cnf mesin yang dipakai, jadi letak TeX Live boleh berbeda di PC lain. Kelas memeriksa
# ketersediaan berkas gaya dengan \IfFileExists (mencari lewat TEXINPUTS), sedangkan bibtex
# mencarinya lewat BSTINPUTS — keduanya memakai entri ini.
BST_TEXLIVE = "$TEXMFDIST/bibtex/bst//"

# Tingkat direktori induk tambahan yang ikut dicari di luar tingkat yang sebenarnya, supaya dokumen
# yang dipindahkan lebih dalam (mis. <proyek>/sub/<dokumen>) tetap terjangkau tanpa menjalankan
# ulang skrip ini. Tingkat yang sebenarnya selalu dicari lebih dahulu.
CADANGAN_INDUK = 2

# Berkas yang menandai sebuah direktori sebagai folder dokumen (punya berkas utama untuk dikompilasi).
PENANDA_DOKUMEN = ("main.tex",)

# Subfolder akar repo yang bukan folder proyek (berisi kelas, pustaka, gambar, skrip, atau hasil).
BUKAN_PROYEK = {"skrip", "uji", "bst", "logo", "referensi", "hasil"}


def akar_repo() -> pathlib.Path:
    """Akar repo template: direktori induk skrip/ tempat skrip ini berada."""
    return pathlib.Path(__file__).resolve().parent.parent


def di_dalam_akar(folder: pathlib.Path, akar: pathlib.Path) -> bool:
    """True bila folder dokumen berada di dalam akar repo (sehingga %DIR% dapat menjangkaunya)."""
    return folder == akar or folder.is_relative_to(akar)


def jalur_induk(folder: pathlib.Path, akar: pathlib.Path, cadangan: int = CADANGAN_INDUK) -> list[str]:
    """Direktori induk folder dokumen, dari folder itu sendiri sampai akar repo, dengan placeholder.

    contoh/skripsi-laporan (2 tingkat di bawah akar repo) menghasilkan %DIR%, %DIR%/..,
    %DIR%/../.., %DIR%/../../.., %DIR%/../../../.. — tingkat yang sebenarnya (dua yang pertama di
    sini) selalu ada, dua tingkat terakhir adalah cadangan supaya salinan dokumen di kedalaman lain
    tetap menemukan akar repo. Untuk akar repo itu sendiri, tingkat 0 = %DIR% sudah tepat.
    """
    tingkat = len(folder.relative_to(akar).parts)
    return [DIR_UTAMA + "/.." * n for n in range(0, tingkat + cadangan + 1)]


def baku_lingkungan(akar: pathlib.Path, folder: pathlib.Path) -> dict[str, str]:
    """Variabel lingkungan yang membuat berkas template di akar repo terjangkau dari folder dokumen.

    Setiap nilai diakhiri ":" supaya jalur bawaan TeX Live tetap ikut dicari (tanpa itu, font dan
    paket sistem tidak ditemukan). Titik di depan berarti "berkas di direktori dokumen menang".

    Untuk folder di dalam repo, semua entri memakai %DIR% sehingga tidak ada jalur PC tertentu.
    Untuk folder di luar repo, jalur absolut akar repo terpaksa dipakai (dan skrip harus dijalankan
    ulang setelah repo dipindahkan).
    """
    if not di_dalam_akar(folder, akar):
        akar_teks = str(akar)
        return {
            "TEXINPUTS": f".:{akar_teks}:{akar_teks}/bst:{akar_teks}/contoh:{akar_teks}/logo:"
                         f"{BST_TEXLIVE}:",
            "BSTINPUTS": f".:{akar_teks}/bst:{BST_TEXLIVE}:",
            "BIBINPUTS": f".:{akar_teks}/referensi:",
        }

    tex, bst, bib = ["."], ["."], ["."]
    for induk in jalur_induk(folder, akar):
        tex += [induk, f"{induk}/bst", f"{induk}/logo", f"{induk}/contoh"]
        bst += [f"{induk}/bst"]
        bib += [f"{induk}/referensi"]
    tex.append(BST_TEXLIVE)
    return {
        "TEXINPUTS": ":".join(tex) + ":",
        "BSTINPUTS": ":".join(bst) + f":{BST_TEXLIVE}:",
        "BIBINPUTS": ":".join(bib) + ":",
    }


def lingkungan_terminal(akar: pathlib.Path, folder: pathlib.Path) -> dict[str, str]:
    """Sama dengan baku_lingkungan, tetapi %DIR% sudah diisi jalur folder.

    Dipakai skrip yang menjalankan pdflatex/qa.py dari terminal (mis. skrip/verifikasi.py): tanpa
    LaTeX Workshop, tidak ada yang mengganti placeholder, jadi nilainya harus diselesaikan lebih
    dulu. Definisi urutan pencariannya tetap satu, di baku_lingkungan().
    """
    return {kunci: nilai.replace(DIR_UTAMA, str(folder))
            for kunci, nilai in baku_lingkungan(akar, folder).items()}


def perintah_bibtex(akar: pathlib.Path, folder: pathlib.Path) -> tuple[str, list[str]]:
    """Perintah tool bibtex pada resep: nama program dan argumennya.

    Skripnya dipanggil lewat program bash, bukan dieksekusi langsung, karena dua hal: jalurnya
    harus absolut (%DIR% dilebarkan LaTeX Workshop, tapi proses dijalankan tanpa shell sehingga "~"
    atau jalur relatif tidak dikembangkan), dan bita executable skrip bisa hilang saat repo
    dipindah (zip, salin lewat Windows) sedangkan bash tetap bisa membacanya.
    """
    if di_dalam_akar(folder, akar):
        naik = "/".join([".."] * len(folder.relative_to(akar).parts))
        skrip = f"{DIR_UTAMA}/{naik}/skrip/bibtex-bila-perlu.sh" if naik else \
            f"{DIR_UTAMA}/skrip/bibtex-bila-perlu.sh"
    else:
        skrip = str(akar / "skrip" / "bibtex-bila-perlu.sh")
    return "bash", [skrip, "%DOCFILE%"]


def setelan(akar: pathlib.Path, folder: pathlib.Path) -> dict:
    """Isi .vscode/settings.json: resep pdflatex -> bibtex -> pdflatex -> pdflatex, build saat simpan.

    Nama tool diberi akhiran -unnes supaya tidak bertabrakan dengan setelan latexmk/biber bawaan
    pengguna; mesin ini tidak memasang latexmk maupun biber, sedangkan template memakai bibtex.
    """
    lingkungan = baku_lingkungan(akar, folder)
    command, args = perintah_bibtex(akar, folder)
    return {
        "latex-workshop.latex.tools": [
            {
                "name": "pdflatex-unnes",
                "command": "pdflatex",
                "args": ["-synctex=1", "-interaction=nonstopmode", "-file-line-error", "%DOC%"],
                "env": lingkungan,
            },
            {
                "name": "bibtex-unnes",
                "command": command,
                "args": args,
                "env": {"BSTINPUTS": lingkungan["BSTINPUTS"],
                        "BIBINPUTS": lingkungan["BIBINPUTS"]},
            },
        ],
        "latex-workshop.latex.recipes": [
            {
                "name": "unnes-ta (pdflatex → bibtex → pdflatex → pdflatex)",
                "tools": ["pdflatex-unnes", "bibtex-unnes", "pdflatex-unnes", "pdflatex-unnes"],
            },
        ],
        "latex-workshop.latex.recipe.default": "first",
        "latex-workshop.latex.build.forceRecipeUsage": True,
        "latex-workshop.latex.autoBuild.run": "onSave",
        "latex-workshop.latex.autoBuild.cleanAndRetry.enabled": True,
        "latex-workshop.latex.autoClean.onBuild": False,
        "latex-workshop.view.pdf.viewer": "tab",
    }


def kepala_setelan(akar: pathlib.Path, folder: pathlib.Path) -> str:
    """Komentar pembuka berkas setelan (settings.json VS Code boleh memuat komentar //)."""
    if di_dalam_akar(folder, akar):
        catatan = [
            "// Setelan ini tidak memuat jalur PC tertentu: semua jalur dibangun dari placeholder %DIR%",
            "// (direktori berkas utama, diisi LaTeX Workshop saat resep berjalan) dan dari $TEXMFDIST",
            "// (dikembangkan kpathsea dari texmf.cnf). Repo boleh dipindah ke PC lain — nama pengguna,",
            "// letak home, dan nama direktori boleh berbeda — dan Ctrl+S tetap bekerja tanpa",
            "// menyunting berkas ini.",
            "//",
            "// Urutan pencarian: direktori dokumen dulu, lalu direktori induknya sampai akar repo (dua",
            "// tingkat di atasnya ikut dicari sebagai cadangan), sehingga identitas.tex atau pustaka",
            "// milik dokumen ini menang atas berkas template.",
            "//",
        ]
    else:
        catatan = [
            "// Dokumen ini berada di luar akar repo template, jadi jalur absolut tidak bisa dihindari",
            "// dan tertulis di setelan bawah ini:",
            f"//   {akar}",
            "// Setelah repo template dipindah, jalankan ulang skrip pembuat setelan ini di PC tersebut:",
            f"//   python3 <akar-baru>/skrip/siapkan-vscode.py {folder}",
            "//",
        ]
    return "\n".join([
        "// Setelan LaTeX Workshop untuk folder dokumen ini — dibuat oleh skrip/siapkan-vscode.py.",
        "//",
        "// Kelas unnes-ta.cls, paket unnes-ta-*.sty, berkas gaya di bst/, pustaka di referensi/, dan",
        "// logo di logo/ ada di akar repo template, bukan di folder ini.",
        *catatan,
        "// Menyunting main.tex atau berkas bab: cukup tekan Ctrl+S. LaTeX Workshop menjalankan resep",
        "// pdflatex -> bibtex -> pdflatex -> pdflatex secara otomatis dan memperbarui main.pdf.",
        "",
    ])



def tulis(folder: pathlib.Path, akar: pathlib.Path) -> pathlib.Path:
    """Menulis <folder>/.vscode/settings.json dan mengembalikan jalurnya."""
    berkas = folder / ".vscode" / "settings.json"
    berkas.parent.mkdir(parents=True, exist_ok=True)
    isi = (kepala_setelan(akar, folder)
           + json.dumps(setelan(akar, folder), indent=2, ensure_ascii=False) + "\n")
    berkas.write_text(isi, encoding="utf-8")
    return berkas


def punya_berkas_utama(folder: pathlib.Path) -> bool:
    """True bila folder berisi main.tex atau berkas .tex lain yang dikompilasi langsung."""
    if not folder.is_dir():
        return False
    if any((folder / nama).exists() for nama in PENANDA_DOKUMEN):
        return True
    return any(folder.glob("*.tex"))


def folder_proyek(akar: pathlib.Path) -> list[pathlib.Path]:
    """Folder proyek: subfolder akar repo yang memuat direktori dokumen (contoh/, harjito/, ...).

    Dikenali dari isinya, bukan dari namanya, sehingga folder proyek baru (mis. proyek_satu/) ikut
    terurus tanpa menyunting skrip ini.
    """
    hasil: list[pathlib.Path] = []
    for dasar in sorted(akar.iterdir()):
        if not dasar.is_dir() or dasar.name.startswith(".") or dasar.name in BUKAN_PROYEK:
            continue
        if (dasar / "identitas.tex").is_file() or any(
                punya_berkas_utama(d) for d in dasar.iterdir() if d.is_dir()):
            hasil.append(dasar)
    return hasil


def folder_bawaan(akar: pathlib.Path) -> list[pathlib.Path]:
    """Akar repo plus setiap folder dokumen di dalam setiap folder proyek dan di uji/."""
    hasil = [akar]
    for proyek in folder_proyek(akar):
        hasil += sorted(d for d in proyek.iterdir() if punya_berkas_utama(d))
    dasar = akar / "uji"
    if dasar.is_dir():
        hasil.append(dasar)
        hasil += sorted(d for d in dasar.iterdir() if punya_berkas_utama(d))
    return hasil


def main() -> int:
    akar = akar_repo()
    pilihan = argparse.ArgumentParser(
        description="Menulis .vscode/settings.json LaTeX Workshop (jalur relatif %DIR%, tanpa "
                    "jalur PC tertentu untuk folder di dalam repo).")
    pilihan.add_argument("folder", nargs="*", type=pathlib.Path,
                         help="folder dokumen yang disetel (bawaan: akar repo + tiap folder "
                              "dokumen di folder proyek dan uji/)")
    pilihan.add_argument("--akar", type=pathlib.Path, default=None,
                         help="akar repo template yang dipakai (bawaan: induk skrip/)")
    arg = pilihan.parse_args()

    akar = (arg.akar or akar).resolve()
    for wajib in ("unnes-ta.cls", "bst", "referensi", "logo"):
        if not (akar / wajib).exists():
            print(f"peringatan: {akar} tidak tampak sebagai akar repo template — "
                  f"{wajib} tidak ada di dalamnya")

    tujuan = [f.resolve() for f in arg.folder] if arg.folder else folder_bawaan(akar)
    jumlah = 0
    luar = 0
    for folder in tujuan:
        if not folder.is_dir():
            print(f"dilewati (bukan direktori): {folder}")
            continue
        if not punya_berkas_utama(folder) and folder != akar:
            print(f"dilewati (tanpa berkas .tex): {folder}")
            continue
        berkas = tulis(folder, akar)
        jalur = berkas.relative_to(akar) if di_dalam_akar(berkas, akar) else berkas
        tanda = "portabel" if di_dalam_akar(folder, akar) else "jalur absolut (di luar repo)"
        print(f"{jalur}  [{tanda}]")
        jumlah += 1
        luar += 0 if di_dalam_akar(folder, akar) else 1

    print(f"\n{jumlah} folder disetel untuk LaTeX Workshop; akar repo = {akar}")
    if luar:
        print(f"perhatian: {luar} folder berada di luar repo, jadi setelannya memuat jalur absolut "
              f"akar repo ini — jalankan ulang skrip ini di PC tempat repo template berada.")
    else:
        print("Setelan portabel: tidak ada jalur absolut, aman bila repo dipindah ke PC lain.")
    print("Tekan Ctrl+S di code-server/VS Code untuk mengompilasi ulang dokumen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
