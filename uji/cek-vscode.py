#!/usr/bin/env python3
"""Memeriksa setelan LaTeX Workshop (.vscode/settings.json) tanpa membuka editor.

Setelan editor tidak dapat diuji dengan mengetik pdflatex dari terminal biasa: justru
LaTeX Workshop yang menyuntikkan TEXINPUTS/BSTINPUTS/BIBINPUTS dari berkas setelan. Skrip ini
menirukan cara kerjanya — membaca daftar tool dan resep dari .vscode/settings.json, mengganti
placeholder seperti %DOC%, %DOCFILE%, %DIR%, dan %WORKSPACE_FOLDER%, menjalankan tiap tool dengan
cwd = direktori dokumen dan lingkungan gabungan (os.environ tanpa TEXINPUTS/BSTINPUTS/BIBINPUTS +
env milik tool) — lalu menghitung galat di main.log. Dengan menghapus variabel warisan itu,
lolosnya pengujian membuktikan berkas setelan sendiri yang cukup, bukan lingkungan shell tempat
pengujian dijalankan.

Dua hal yang diperiksa:

1. Kompilasi: resep pdflatex -> bibtex -> pdflatex -> pdflatex berjalan tanpa galat dan
   menghasilkan main.pdf.
2. Portabilitas: tidak ada jalur milik PC ini (mis. /home/<pengguna>/... atau ~/latex/...) yang
   tertulis di setelan. Setelan yang portabel dibangun dari %DIR% (diisi LaTeX Workshop) dan
   $TEXMFDIST (dikembangkan kpathsea), sehingga repo tetap bekerja setelah dipindah ke PC lain.
   Folder dokumen di luar akar repo memang memakai jalur absolut; untuk itu dilaporkan sebagai
   "jalur PC (di luar repo)" dan tidak dianggap gagal.

Pemakaian (dijalankan dari akar repo):
    python3 uji/cek-vscode.py                                  # semua folder ber-.vscode
    python3 uji/cek-vscode.py contoh/skripsi-laporan           # folder tertentu
    python3 uji/cek-vscode.py --draft <folder>                 # satu pass tanpa PDF (lebih cepat)
    python3 uji/cek-vscode.py --workspace=akar                 # folder yang dibuka = akar repo
    python3 uji/cek-vscode.py --bersih                          # hapus berkas bantu, tidak mengompilasi
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

AKAR = pathlib.Path(__file__).resolve().parent.parent
PERLU_DIBUANG = ("TEXINPUTS", "BSTINPUTS", "BIBINPUTS")   # disetel berkas .vscode, bukan warisan shell

# Jalur milik PC ini: "/..." di awal nilai atau sesudah pemisah jalur, dan "~/".
# Tidak menyalahkan entri seperti %DIR%/../.. atau $TEXMFDIST/bibtex/bst// yang memang portabel.
POLA_JALUR_PC = re.compile(r"(?:^|[:=\s])~/|(?:^|[:=\s])/[^/:\s]")


def baca_setelan(folder: pathlib.Path) -> dict:
    """Membaca .vscode/settings.json (komentar // diabaikan seperti di VS Code)."""
    berkas = folder / ".vscode" / "settings.json"
    teks = berkas.read_text(encoding="utf-8")
    tanpa_komentar = "\n".join(re.sub(r"^\s*//.*$", "", baris) for baris in teks.splitlines())
    return json.loads(tanpa_komentar)


def ganti_placeholder(teks: str, folder: pathlib.Path, workspace: pathlib.Path) -> str:
    """Menirukan replaceArgumentPlaceholders milik LaTeX Workshop (out/src/utils/utils.js).

    Placeholder diisi sama seperti ekstensi: %DOC% tanpa ekstensi, %DOCFILE% nama pokok berkas,
    %DIR% direktori berkas utama, %WORKSPACE_FOLDER% folder yang dibuka di code-server/VS Code.
    """
    main = folder / "main.tex"
    return (teks.replace("%DOCFILE_EXT%", main.name)
                 .replace("%DOC_EXT%", str(main))
                 .replace("%DOCFILE%", main.stem)
                 .replace("%DOC%", str(main.with_suffix("")))
                 .replace("%DIR%", str(folder))
                 .replace("%WORKSPACE_FOLDER%", str(workspace))
                 .replace("%RELATIVE_DIR%", str(folder.relative_to(workspace)) if
                          folder.is_relative_to(workspace) else str(folder))
                 .replace("%RELATIVE_DOC%", str(main.relative_to(workspace)) if
                          main.is_relative_to(workspace) else str(main)))


def lingkungan_tool(tool: dict) -> dict[str, str]:
    """Lingkungan proses untuk satu tool: variabel warisan TEXINPUTS dkk. dibuang lebih dulu."""
    dasar = {k: v for k, v in os.environ.items() if k not in PERLU_DIBUANG}
    dasar.update(tool.get("env", {}))
    return dasar


def jalur_pc(setelan: dict) -> list[str]:
    """Nilai setelan yang memuat jalur milik PC ini (tidak portabel) beserta nama toolnya."""
    temuan: list[str] = []
    for tool in setelan["latex-workshop.latex.tools"]:
        nilai = [tool["command"], *tool.get("args", []), *tool.get("env", {}).values()]
        for t in nilai:
            if POLA_JALUR_PC.search(t):
                temuan.append(f"{tool['name']}: {t}")
    return temuan


def jalankan_resep(folder: pathlib.Path, setelan: dict, workspace: pathlib.Path,
                   draft: bool = False) -> tuple[int, list[str]]:
    """Menjalankan resep pertama di folder dokumen; mengembalikan (jumlah galat, pesan).

    Jumlah galat -1 berarti folder dilewati karena tidak punya main.tex (mis. akar repo atau
    direktori uji yang berkasnya diperiksa uji/cek-*.py).
    """
    main = folder / "main.tex"
    if not main.is_file():
        return -1, ["tidak ada main.tex di folder ini"]

    tool = {t["name"]: t for t in setelan["latex-workshop.latex.tools"]}
    resep = setelan["latex-workshop.latex.recipes"][0]
    pesan: list[str] = []

    for nama in resep["tools"]:
        t = tool[nama]
        isi = ganti_placeholder
        args = [isi(a, folder, workspace) for a in t["args"]]
        if draft:
            args = args[:1] + ["-draftmode"] + args[1:]
        command = isi(t["command"], folder, workspace)
        env = {k: isi(v, folder, workspace) for k, v in t.get("env", {}).items()}
        hasil = subprocess.run([command, *args], cwd=folder, capture_output=True, text=True,
                               env=lingkungan_tool({"env": env}))
        pesan.append(f"{command} -> kode {hasil.returncode}")
        if hasil.returncode != 0 and not draft:
            pesan.append(f"  keluaran: {(hasil.stdout + hasil.stderr).strip().splitlines()[-1:] or ['']}")

    log = folder / f"{main.stem}.log"
    galat = 0
    if log.is_file():
        teks = log.read_text(encoding="utf-8", errors="replace")
        galat = len(re.findall(r"^! ", teks, flags=re.M))
        for pola in ("tidak ditemukan", "not found", "No file"):
            for baris in re.findall(rf"^.*{pola}.*$", teks, flags=re.M):
                if "log" not in baris.lower():
                    pesan.append(f"  {baris.strip()[:110]}")
    return galat, pesan


def bersihkan(folder: pathlib.Path) -> None:
    """Menghapus berkas bantu kompilasi di satu folder dokumen."""
    for pola in ("*.aux", "*.log", "*.toc", "*.lof", "*.lot", "*.loa", "*.out", "*.bbl", "*.blg",
                 "*.spl", "*.fls", "*.fdb_latexmk", "*.synctex.gz"):
        for berkas in folder.glob(pola):
            berkas.unlink()


def main() -> int:
    arg = sys.argv[1:]
    draft = "--draft" in arg
    bersih = "--bersih" in arg
    workspace_arg = next((a.split("=", 1)[1] for a in arg if a.startswith("--workspace=")), "")
    arg = [a for a in arg if not a.startswith("--")]

    if arg:
        folder_dokumen = [(AKAR / a if not pathlib.Path(a).is_absolute() else pathlib.Path(a)).resolve()
                          for a in arg]
    else:
        folder_dokumen = sorted({b.parent.parent for b in AKAR.glob("**/.vscode/settings.json")})

    if bersih:
        for folder in folder_dokumen:
            bersihkan(folder)
        print(f"berkas bantu dibersihkan di {len(folder_dokumen)} folder.")
        return 0

    gagal = 0
    diuji = 0
    dilewat = 0
    jalur_absolut = 0
    for folder in folder_dokumen:
        if not (folder / ".vscode" / "settings.json").is_file():
            print(f"LEWAT  {folder}: .vscode/settings.json tidak ada")
            gagal += 1
            continue
        # Folder yang dibuka di editor: folder dokumen sendiri (bawaan) atau akar repo, karena
        # setelan yang sama harus benar pada kedua cara membuka repo.
        if workspace_arg in ("akar", "root"):
            workspace = AKAR
        elif workspace_arg:
            workspace = (AKAR / workspace_arg).resolve()
        else:
            workspace = folder
        setelan = baca_setelan(folder)

        temuan = jalur_pc(setelan)
        dalam_repo = folder.is_relative_to(AKAR)
        if temuan and dalam_repo:
            print(f"JALUR PC  {folder}  (setelan tidak portabel, seharusnya memakai %DIR%)")
            for baris in temuan:
                print(f"        {baris}")
            gagal += 1
        elif temuan:
            jalur_absolut += 1

        galat, pesan = jalankan_resep(folder, setelan, workspace, draft=draft)
        if galat < 0:
            print(f"LEWAT  {folder}: {pesan[0]} (bukan folder dokumen)")
            dilewat += 1
            continue
        diuji += 1
        pdf = folder / "main.pdf"
        status = "OK   " if galat == 0 else "GAGAL"
        print(f"{status} {folder}  (workspace={workspace})")
        for baris in pesan:
            print(f"        {baris}")
        if not draft:
            print(f"        main.pdf {'ada' if pdf.is_file() else 'TIDAK ADA'}"
                  f"{'' if not pdf.is_file() else f', {pdf.stat().st_size} bita'}")
        if galat != 0:
            gagal += 1

    print(f"\ndiuji: {diuji} folder, dilewati: {dilewat}, jalur PC (di luar repo): {jalur_absolut}, "
          f"gagal: {gagal}")
    return 1 if gagal else 0


if __name__ == "__main__":
    raise SystemExit(main())
