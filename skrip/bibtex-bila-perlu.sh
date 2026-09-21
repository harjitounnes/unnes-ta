#!/usr/bin/env bash
# skrip/bibtex-bila-perlu.sh — menjalankan bibtex hanya bila berkas .aux memang memuat \bibdata.
#
# Dipakai resep LaTeX Workshop (.vscode/settings.json) sebagai ganti pemanggilan bibtex langsung:
# dokumen tanpa daftar pustaka — mis. contoh/publikasi-repositori yang menurut panduan hal. 59
# tidak memuat isi artikel — tidak punya \bibdata di main.aux, dan bibtex akan keluar dengan galat
# "(There were 3 error messages)" yang menghentikan resep walaupun dokumennya sendiri baik-baik saja.
#
# Pemakaian:
#   skrip/bibtex-bila-perlu.sh              menyusun pustaka main.aux
#   skrip/bibtex-bila-perlu.sh <nama>       untuk berkas utama bernama lain (mis. uji-fase3)
#
# BSTINPUTS/BIBINPUTS disetel pemanggil (LaTeX Workshop atau kompilasi.sh dokumen salinan).
set -uo pipefail

berkas="${1:-main}"

if [ ! -f "$berkas.aux" ]; then
  echo "bibtex dilewati: $berkas.aux belum ada."
  exit 0
fi

if ! grep -q 'bibdata' "$berkas.aux"; then
  echo "bibtex dilewati: $berkas.aux tidak memuat \\bibdata (dokumen ini tanpa daftar pustaka)."
  exit 0
fi

bibtex "$berkas"
