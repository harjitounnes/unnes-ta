#!/usr/bin/env python3
"""Menyalin satu dokumen contoh menjadi dokumen mandiri yang siap disunting.

Dokumen contoh tidak berdiri sendiri: kelas unnes-ta.cls, paket unnes-ta-*.sty, berkas gaya
bst/unnes-apalike-apa.bst, pustaka referensi/contoh.bib, logo, dan data identitas bersama
contoh/identitas.tex ada di akar repo, sehingga main.tex memakai rujukan berjalur relatif
(\\input{../identitas}, \\daftarpustaka{../../referensi/contoh}, logodir=../../logo). Begitu
direktori contoh disalin ke tempat lain, rujukan itu tidak lagi terjangkau dan kompilasi berhenti
dengan galat.

Skrip ini menyalin dokumen sekaligus membereskan rujukannya:

  1. isi direktori contoh disalin ke direktori tujuan tanpa berkas bantu kompilasi
     (.aux/.log/.pdf/... dari kompilasi sebelumnya);
  2. setiap rujukan diperiksa dari direktori tujuan. Yang tidak terjangkau diganti dengan rujukan
     lokal, dan berkas sumbernya disalin ke tujuan bila perlu:
        \\input{../identitas}                   -> \\input{identitas}    + identitas.tex
        \\daftarpustaka{../../referensi/contoh} -> \\daftarpustaka{pustaka} + pustaka.bib
        logodir=../../logo                      -> logodir=logo          (dicari lewat TEXINPUTS)
  3. .vscode/settings.json ditulis lewat skrip/siapkan-vscode.py, jadi menekan Ctrl+S di
     code-server/VS Code langsung mengompilasi ulang dokumen (pdflatex -> bibtex -> pdflatex ->
     pdflatex) tanpa galat jalur relatif;
  4. kompilasi.sh ditulis untuk pemakaian di terminal (menyetel TEXINPUTS/BSTINPUTS/BIBINPUTS yang
     sama dengan setelan editor).

Dokumen hasil salinan masih memakai kelas dan paket dari repo template lewat TEXINPUTS, sehingga
perbaikan kelas otomatis ikut terpakai. Bila dokumen tujuan masih berada DI DALAM repo (mis.
`contoh/` -> `proyek_satu/skripsi-laporan`), setelannya tetap tanpa jalur PC tertentu dan jalan
terus walau repo dipindah ke PC lain. Bila dokumen disalin ke LUAR repo (mis. `~/tugas-akhir-saya`),
akar repo tidak bisa dijangkau jalur relatif: jalur absolutnya tertulis di .vscode/settings.json
dan di kompilasi.sh — setelah repo template dipindah, jalankan ulang skrip ini di PC tersebut.

Pemakaian:
    python3 skrip/salin-dokumen.py contoh/skripsi-laporan ~/tugas-akhir-saya
    python3 skrip/salin-dokumen.py contoh/prototipe-laporan tugas-akhir-saya   # tetap di dalam repo
    python3 skrip/salin-dokumen.py contoh/skripsi-laporan ~/ta --paksa         # timpa tujuan yang ada
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import shutil

# Berkas hasil kompilasi yang tidak perlu ikut disalin (gambar/*.pdf tetap ikut: itu aset dokumen).
AKHIRAN_BANTU = {".aux", ".log", ".toc", ".lof", ".lot", ".loa", ".out", ".bbl", ".blg", ".spl",
                 ".fls", ".fdb_latexmk", ".synctex.gz", ".pyc"}
NAMA_BANTU = {"main.pdf", "main.synctex.gz"}

# Baris komentar lama di main.tex yang menyebut jalur relatif ../.. — diganti petunjuk kompilasi baru.
BARIS_BUANG = ("%% Kompilasi dijalankan dari direktori ini", "%%   TEXINPUTS=../..",
               "%%   pdflatex -interaction", "%% Seluruh contoh sekaligus",
               "%% Kompilasi dari direktori ini:", "%% Ctrl+S bila disunting",
               "%% BSTINPUTS, dan BIBINPUTS ke akar repo")
KOMENTAR_BARU = (
    "%% Kompilasi dari direktori ini: ./kompilasi.sh  (di code-server/VS Code cukup Ctrl+S;\n"
    "%% .vscode/settings.json sudah menyuntikkan TEXINPUTS/BSTINPUTS/BIBINPUTS ke repo template).\n")

KEPALA_KOMPILASI = """#!/usr/bin/env bash
# kompilasi.sh — mengompilasi main.tex dokumen ini dari terminal.
#
#   ./kompilasi.sh            pdflatex -> bibtex -> pdflatex -> pdflatex (menghasilkan main.pdf)
#   ./kompilasi.sh --draft    satu pass tanpa PDF (memeriksa galat dengan cepat)
#   ./kompilasi.sh --bersih   hapus berkas bantu kompilasi, tidak mengompilasi
#
# Kelas unnes-ta.cls, paket unnes-ta-*.sty, berkas gaya BibTeX, pustaka, dan logo template ada di
# akar repo:
#   {{AKAR}}
# Variabel di bawah menyuntikkan direktori itu, jadi dokumen ini bisa dikompilasi dari mana pun.
# Bila dokumen ini masih berada di dalam repo, nilainya berjalan sendiri lewat direktori dokumen
# (tanpa jalur PC tetap); bila berada di luar repo, jalur absolut di atas yang dipakai.
# Titik di depan berarti berkas di direktori ini (identitas.tex, pustaka.bib, kelas lokal) selalu
# dipakai lebih dahulu daripada berkas template.
#
# Menyunting di code-server/VS Code tidak memerlukan skrip ini — .vscode/settings.json sudah
# menyetel hal yang sama dan mengompilasi otomatis saat berkas disimpan.
set -uo pipefail
cd "$(dirname "$0")"
dir_dokumen="$(pwd)"

# Akar repo template: dicari dari direktori dokumen (dua tingkat di atas), lalu jatuh ke jalur
# terekam di atas — supaya dokumen yang sudah di luar repo tetap tahu di mana kelasnya.
akar="{{AKAR}}"
for kandidat in "$dir_dokumen/../.." "$dir_dokumen/.." "$dir_dokumen"; do
  if [ -f "$kandidat/unnes-ta.cls" ]; then akar="$kandidat"; break; fi
done
[ -f "$akar/unnes-ta.cls" ] || echo "peringatan: unnes-ta.cls tidak ditemukan (akar repo = $akar);" \
  "jalankan ulang skrip/salin-dokumen.py di PC ini bila repo template sudah dipindah." >&2

export TEXINPUTS="{{TEXINPUTS}}"
export BSTINPUTS="{{BSTINPUTS}}"
export BIBINPUTS="{{BIBINPUTS}}"

draft=0
bersih=0
for arg in "$@"; do
  case "$arg" in
    --draft)  draft=1 ;;
    --bersih) bersih=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "opsi tidak dikenal: $arg (lihat --help)" >&2; exit 2 ;;
  esac
done

if [ "$bersih" = 1 ]; then
  rm -f ./*.aux ./*.log ./*.toc ./*.lof ./*.lot ./*.loa ./*.out ./*.bbl ./*.blg ./*.spl \\
        ./*.fls ./*.fdb_latexmk ./*.synctex.gz 2>/dev/null
  echo "berkas bantu kompilasi dihapus."
  exit 0
fi

if [ "$draft" = 1 ]; then
  pdflatex -interaction=nonstopmode -draftmode main.tex > main.log 2>&1 || true
else
  pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
  if [ -f main.aux ] && grep -q bibdata main.aux; then bibtex main >/dev/null 2>&1; fi
  pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
  pdflatex -interaction=nonstopmode main.tex > main.log 2>&1 || true
fi

galat=0
if [ -f main.log ]; then
  galat=$(grep -c '^! ' main.log 2>/dev/null) || galat=0
  galat=${galat:-0}
  halaman=$(grep -o '([0-9]* pages' main.log | tail -1 | tr -d '(')
fi
if [ "$draft" = 1 ]; then
  echo "main.tex: draft tanpa PDF, galat=$galat"
elif [ "$galat" = 0 ]; then
  echo "main.tex: main.pdf terbaru, ${halaman:-hasil tidak diketahui}, galat=0"
else
  echo "main.tex: galat=$galat — periksa main.log" >&2
fi
[ "$galat" = 0 ]
"""


def akar_repo() -> pathlib.Path:
    """Akar repo template: direktori induk skrip/ tempat skrip ini berada."""
    return pathlib.Path(__file__).resolve().parent.parent


def muat_siapkan_vscode():
    """Memuat skrip/siapkan-vscode.py (nama berkas memakai tanda hubung, jadi dimuat manual)."""
    berkas = pathlib.Path(__file__).resolve().parent / "siapkan-vscode.py"
    spesifikasi = importlib.util.spec_from_file_location("siapkan_vscode", berkas)
    modul = importlib.util.module_from_spec(spesifikasi)
    spesifikasi.loader.exec_module(modul)
    return modul


def abaikan(akar_salinan: str, isi: list[str]) -> set[str]:
    """Berkas/folder yang dilewati saat menyalin: hasil kompilasi dan .vscode lama."""
    buang = set()
    for nama in isi:
        jalur = pathlib.Path(akar_salinan) / nama
        if jalur.is_dir():
            if nama == ".vscode":
                buang.add(nama)
        elif jalur.is_file() and (jalur.suffix in AKHIRAN_BANTU or nama in NAMA_BANTU):
            buang.add(nama)
    return buang


def berkas_sumber(arg: str, akar: pathlib.Path, akhiran: str, cadangan: tuple[str, ...]) -> pathlib.Path | None:
    """Mencari berkas yang dirujuk main.tex: jalurnya sendiri, lalu di dalam direktori cadangan."""
    kandidat = [akar / f"{arg}{akhiran}"]
    kandidat += [akar / sub / f"{pathlib.Path(arg).name}{akhiran}" for sub in cadangan]
    for k in kandidat:
        if k.is_file():
            return k
    return None


def perbaiki_rujukan(isi: str, tujuan: pathlib.Path, akar: pathlib.Path,
                     ) -> tuple[str, list[str], list[tuple[pathlib.Path, pathlib.Path]]]:
    """Mengganti rujukan main.tex yang tidak terjangkau dari direktori tujuan.

    Mengembalikan (isi baru, catatan perubahan, daftar berkas yang perlu disalin ke tujuan).
    """
    catatan: list[str] = []
    salinan: list[tuple[pathlib.Path, pathlib.Path]] = []

    def terjangkau(arg: str, akhiran: str) -> bool:
        return (tujuan / f"{arg}{akhiran}").is_file()

    # 1) data identitas bersama: \input{../identitas}
    for cocok in re.finditer(r"\\input\{([^}]*identitas[^}]*)\}", isi):
        arg = cocok.group(1)
        if terjangkau(arg, ".tex"):
            continue
        sumber = berkas_sumber(arg, akar, ".tex", ("contoh",))
        if sumber is None:
            catatan.append(f"identitas: berkas {arg}.tex tidak ditemukan di akar repo — dilewati")
            continue
        rujukan_baru = "identitas"
        if not (tujuan / "identitas.tex").is_file():
            salinan.append((sumber, tujuan / "identitas.tex"))
        isi = isi.replace(f"\\input{{{arg}}}", f"\\input{{{rujukan_baru}}}")
        # Komentar pengantar main.tex masih menyebut berkas identitas bersama di ../identitas.tex.
        isi = isi.replace(
            "%% Data identitas seluruh contoh ada di satu berkas: ../identitas.tex (dipakai bersama oleh\n"
            "%% contoh proposal, laporan, maupun repositori).\n",
            "%% Data identitas dokumen ini ada di identitas.tex di direktori ini (salinan dari\n"
            "%% contoh/identitas.tex); sunting bebas, dokumen lain tidak ikut berubah.\n")
        isi = isi.replace(
            "%% Data identitas bersama diambil dari ../identitas.tex. Baris di bawah hanya menambah atau\n"
            "%% menimpa data bersama itu untuk dokumen ini (judul, gelar, pembimbing/penguji tambahan).\n",
            "%% Baris di bawah menambah atau menimpa data identitas di atas untuk dokumen ini\n"
            "%% (judul, gelar, pembimbing/penguji tambahan).\n")
        catatan.append(f"\\input{{{arg}}} -> \\input{{{rujukan_baru}}} "
                       f"(isinya disalin dari {sumber.relative_to(akar)}; sunting bebas)")

    # 2) pustaka: \daftarpustaka{../../referensi/contoh}
    for cocok in re.finditer(r"\\daftarpustaka\{([^}]*)\}", isi):
        arg = cocok.group(1)
        if terjangkau(arg, ".bib"):
            continue
        sumber = berkas_sumber(arg, akar, ".bib", ("referensi",))
        if sumber is None:
            catatan.append(f"pustaka: berkas {arg}.bib tidak ditemukan — dilewati")
            continue
        if not (tujuan / "pustaka.bib").is_file():
            salinan.append((sumber, tujuan / "pustaka.bib"))
        isi = isi.replace(f"\\daftarpustaka{{{arg}}}", "\\daftarpustaka{pustaka}")
        catatan.append(f"\\daftarpustaka{{{arg}}} -> \\daftarpustaka{{pustaka}} "
                       f"(pustaka.bib disalin dari {sumber.relative_to(akar)}; tambahkan entri di sini)")

    # 3) logo: opsi kelas logodir=../../logo (dicari lewat TEXINPUTS bila diset logodir=logo)
    for cocok in re.finditer(r"logodir=([^,\]]+)", isi):
        arg = cocok.group(1)
        if (tujuan / arg).is_dir():
            continue
        isi = isi.replace(f"logodir={arg}", "logodir=logo")
        catatan.append(f"logodir={arg} -> logodir=logo (logo/logo-unnes.* dicari lewat TEXINPUTS "
                       f"ke {akar / 'logo'})")

    return isi, catatan, salinan


def rapikan_komentar(isi: str) -> str:
    """Mengganti baris komentar lama di main.tex yang menyebut jalur ../.. dan skrip/build.sh."""
    keluaran: list[str] = []
    baru_disiapkan = False
    for baris in isi.splitlines(keepends=True):
        if baris.startswith(BARIS_BUANG):
            if not baru_disiapkan:
                keluaran.append(KOMENTAR_BARU)
                baru_disiapkan = True
            continue
        keluaran.append(baris)
    return "".join(keluaran)


def main() -> int:
    akar = akar_repo()
    pilihan = argparse.ArgumentParser(
        description="Menyalin contoh menjadi dokumen mandiri beserta setelan editor.")
    pilihan.add_argument("sumber", type=pathlib.Path, help="direktori contoh, mis. contoh/skripsi-laporan")
    pilihan.add_argument("tujuan", type=pathlib.Path, help="direktori dokumen baru")
    pilihan.add_argument("--paksa", action="store_true",
                         help="timpa direktori tujuan yang sudah berisi dokumen")
    arg = pilihan.parse_args()

    sumber = (akar / arg.sumber if not arg.sumber.is_absolute() else arg.sumber).resolve()
    tujuan = (pathlib.Path.cwd() / arg.tujuan if not arg.tujuan.is_absolute() else arg.tujuan).resolve()

    if not (sumber / "main.tex").is_file():
        print(f"galat: {sumber} bukan direktori dokumen contoh (main.tex tidak ada)")
        return 1
    if sumber == tujuan:
        print("galat: direktori sumber dan tujuan sama")
        return 1
    if (tujuan / "main.tex").is_file() and not arg.paksa:
        print(f"galat: {tujuan} sudah berisi dokumen (main.tex ada). Pakai --paksa untuk menimpa.")
        return 1
    if tujuan.exists() and arg.paksa:
        shutil.rmtree(tujuan)
    tujuan.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(sumber, tujuan, ignore=abaikan, dirs_exist_ok=True)

    berkas_main = tujuan / "main.tex"
    isi = rapikan_komentar(berkas_main.read_text(encoding="utf-8"))
    isi, catatan, salinan = perbaiki_rujukan(isi, tujuan, akar)
    berkas_main.write_text(isi, encoding="utf-8")

    for asal, ke in salinan:
        if not ke.exists():
            shutil.copy2(asal, ke)

    siapkan_vscode = muat_siapkan_vscode()
    berkas_setelan = siapkan_vscode.tulis(tujuan, akar)

    berkas_kompilasi = tujuan / "kompilasi.sh"
    lingkungan = siapkan_vscode.baku_lingkungan(akar, tujuan)
    isi_kompilasi = KEPALA_KOMPILASI.replace("{{AKAR}}", str(akar))
    for kunci in ("TEXINPUTS", "BSTINPUTS", "BIBINPUTS"):
        # Nilai $TEXMFDIST harus sampai ke kpathsea apa adanya: didahului \ supaya shell tidak
        # mengembangkannya lebih dulu (di PC tanpa variabel itu hasilnya justru jalur kosong).
        nilai = lingkungan[kunci].replace("$", r"\$").replace("%DIR%", "$dir_dokumen")
        isi_kompilasi = isi_kompilasi.replace(f"{{{{{kunci}}}}}", nilai)
    berkas_kompilasi.write_text(isi_kompilasi, encoding="utf-8")
    berkas_kompilasi.chmod(0o755)

    print(f"dokumen disalin: {sumber} -> {tujuan}")
    for baris in catatan:
        print(f"  rujukan: {baris}")
    for asal, ke in salinan:
        print(f"  disalin: {asal.relative_to(akar)} -> {ke.relative_to(tujuan)}")
    print(f"  setelan editor: {berkas_setelan.relative_to(tujuan)} (Ctrl+S mengompilasi ulang)")
    print(f"  terminal: {berkas_kompilasi.relative_to(tujuan)}")
    print(f"\nBerikutnya: cd {tujuan} && ./kompilasi.sh  — lalu sunting main.tex dan bab/ sesuka Anda.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
