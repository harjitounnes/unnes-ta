#!/usr/bin/env bash
# skrip/build.sh — mengompilasi dokumen di satu atau beberapa folder proyek.
#
# Pemakaian:
#   skrip/build.sh                        kompilasi semua dokumen di contoh/ (bawaan)
#   skrip/build.sh proyek_satu            kompilasi semua dokumen di proyek_satu/, bukan contoh/
#   skrip/build.sh harjito proyek_satu    dua folder proyek sekaligus
#   skrip/build.sh harjito/skripsi-laporan   hanya satu dokumen (folder berisi main.tex)
#   skrip/build.sh proyek_satu --only=skripsi-laporan
#   skrip/build.sh proyek_satu --engine=lualatex
#   skrip/build.sh proyek_satu --draft     satu pass tanpa keluaran PDF (memeriksa galat cepat)
#   skrip/build.sh proyek_satu --bersih    hapus berkas bantu (.aux/.log/.bbl/.toc/...), tanpa kompilasi
#
# Parameternya adalah folder proyek: subfolder akar repo yang memuat direktori dokumen (contoh/,
# harjito/, proyek_satu/, ...) atau langsung satu direktori dokumen yang berisi main.tex. Nama boleh
# ditulis relatif terhadap akar repo maupun sebagai jalur dari direktori kerja. Tanpa parameter
# dipakai contoh/.
#
# Direktori bst/ template harus terjangkau: TEXINPUTS dipakai kelas untuk memeriksa berkas gaya
# BibTeX, BSTINPUTS dipakai bibtex untuk menemukannya.
set -uo pipefail

akar="$(cd "$(dirname "$0")/.." && pwd)"
mesin="pdflatex"
hanya=""
draft=0
bersih=0
sasaran=()

for arg in "$@"; do
  case "$arg" in
    --only=*)   hanya="${arg#--only=}" ;;
    --engine=*) mesin="${arg#--engine=}" ;;
    --draft)    draft=1 ;;
    --bersih)   bersih=1 ;;
    -h|--help)  sed -n '2,20p' "$0"; exit 0 ;;
    -*)         echo "opsi tidak dikenal: $arg (lihat --help)" >&2; exit 2 ;;
    *)          sasaran+=("$arg") ;;
  esac
done

[ ${#sasaran[@]} -gt 0 ] || sasaran=(contoh)

# Direktori kelas/paket, berkas gaya BibTeX, data identitas bersama, pustaka, dan logo template
# semuanya ada di akar repo. Variabel di bawah menyuntikkannya ke kompilasi, sama dengan yang
# disetel .vscode/settings.json (lihat skrip/siapkan-vscode.py), supaya hasil kompilasi terminal dan
# editor identik. Titik di depan: berkas di direktori dokumen dipakai lebih dahulu.
bawaan_bst=""
if command -v kpsewhich >/dev/null 2>&1; then
  texmfdist="$(kpsewhich --var-value TEXMFDIST 2>/dev/null || true)"
  [ -n "$texmfdist" ] && [ -d "$texmfdist/bibtex/bst" ] && bawaan_bst="$texmfdist/bibtex/bst//"
fi

export TEXINPUTS=".:$akar:$akar/bst:$akar/contoh:$akar/logo${bawaan_bst:+:$bawaan_bst}:${TEXINPUTS:-}"
export BSTINPUTS=".:$akar/bst:${BSTINPUTS:-}"
export BIBINPUTS=".:$akar/referensi:${BIBINPUTS:-}"

bersihkan() {  # hapus berkas bantu di satu direktori
  rm -f "$1"/*.aux "$1"/*.log "$1"/*.toc "$1"/*.lof "$1"/*.lot "$1"/*.loa "$1"/*.out \
        "$1"/*.bbl "$1"/*.blg "$1"/*.spl "$1"/*.fls "$1"/*.fdb_latexmk "$1"/*.synctex.gz 2>/dev/null
}

# Kumpulkan direktori dokumen dari setiap sasaran: folder proyek (semua subfolder ber-main.tex)
# atau satu direktori dokumen. Ditulis sebagai "label<TAB>direktori" agar nama proyek tetap terlihat.
daftar=()
for s in "${sasaran[@]}"; do
  dir="$s"
  [ -d "$dir" ] || dir="$akar/$s"
  if [ ! -d "$dir" ]; then
    echo "galat: folder '$s' tidak ada (dicari juga di $akar/$s)" >&2
    exit 2
  fi
  if [ -f "$dir/main.tex" ]; then
    daftar+=("$s	$dir")
    continue
  fi
  ada=0
  for d in "$dir"/*/; do
    d="${d%/}"
    [ -f "$d/main.tex" ] || continue
    ada=1
    daftar+=("$s/$(basename "$d")	$d")
  done
  if [ "$ada" = 0 ]; then
    echo "galat: tidak ada dokumen (main.tex) di $dir" >&2
    exit 2
  fi
done

if [ "$bersih" = 1 ]; then
  for baris in "${daftar[@]}"; do
    bersihkan "${baris#*	}"
  done
  for d in "$akar"/uji "$akar"/uji/sistematika "$akar"/uji/sitasi; do
    [ -d "$d" ] && bersihkan "$d"
  done
  echo "berkas bantu di ${#daftar[@]} direktori dokumen dan uji/ dibersihkan."
  exit 0
fi

total=0; gagal=0
for baris in "${daftar[@]}"; do
  label="${baris%%	*}"; d="${baris#*	}"
  nama="$(basename "$d")"
  [ -n "$hanya" ] && [ "$nama" != "$hanya" ] && continue
  total=$((total + 1))
  (
    cd "$d" || exit 1
    if [ "$draft" = 1 ]; then
      "$mesin" -interaction=nonstopmode -draftmode main.tex > main.log 2>&1
    else
      "$mesin" -interaction=nonstopmode main.tex >/dev/null 2>&1
      if [ -f main.aux ] && grep -q bibdata main.aux; then bibtex main >/dev/null 2>&1; fi
      "$mesin" -interaction=nonstopmode main.tex >/dev/null 2>&1
      "$mesin" -interaction=nonstopmode main.tex > main.log 2>&1
    fi
  )
  galat="?"
  if [ -f "$d/main.log" ]; then
    galat=$(grep -c '^! ' "$d/main.log" 2>/dev/null) || galat=0
    galat=${galat:-0}
    hal=$(grep -o '([0-9]* pages' "$d/main.log" | tail -1)
    hal=${hal:-"(draft: tanpa PDF)"}
  fi
  printf '%-32s mesin=%-9s error=%-3s %s\n' "$label" "$mesin" "$galat" "$hal"
  [ "$galat" != "0" ] && gagal=$((gagal + 1))
done

echo
echo "dokumen dikompilasi: $total, gagal: $gagal"

[ "$gagal" = 0 ]
