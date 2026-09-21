%% unnes-ta.cls — kelas dokumen Tugas Akhir Universitas Negeri Semarang (panduan 2024)
%% Penulis: template modular; lihat README.md dan PEMETAAN-PANDUAN.md
%% Kelas ini HANYA mengurus: opsi, validasi, pemuatan paket, dan urutan pemuatan.
%% Aturan format ada di paket-paket terpisah (unnes-ta-*.sty).

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{unnes-ta}[2026/09/20 v0.1 Kelas dokumen Tugas Akhir UNNES]

%====================================================================== opsi
\RequirePackage{kvoptions}
\RequirePackage{iftex}
\RequirePackage{etoolbox}
\SetupKeyvalOptions{family=unnes,prefix=unnes@}

\DeclareStringOption[skripsi]{jenis}     % skripsi|proyek|prototipe|publikasi|prestasi
\DeclareStringOption[laporan]{mode}      % proposal|laporan|repositori
\DeclareStringOption[sarjana]{jenjang}   % sarjana|diploma
\DeclareStringOption[apa]{sitasi}        % apa|ieee|mla|chicago|harvard|acs
\DeclareStringOption[]{sitasibst}        % kosong = otomatis dari preset sitasi;
                                         % isi dengan berkas .bst resmi prodi/jurnal bila ada
\DeclareStringOption[id]{bahasa}         % id|en  (id = nama bab/tabel/gambar berbahasa Indonesia)
\DeclareStringOption[bawah]{halaman}     % bawah|atas
\DeclareStringOption[3cm]{ukuranlogo}    % sisi kotak logo, logo wajib P:L = 1:1
\DeclareStringOption[logo]{logodir}      % direktori berkas logo (relatif ke berkas utama)
\DeclareStringOption[logo-unnes]{logo}   % nama berkas logo tanpa ekstensi (dicari .pdf lalu .png lalu .jpg)
\DeclareStringOption[]{spasi}            % kosong = otomatis menurut mode (1,5 / 1,15 / 1,0)
\DeclareBoolOption[false]{duasisi}
\DeclareBoolOption[false]{draft}
\DeclareBoolOption[true]{catatan}        % cetak catatan panduan pada kerangka sistematika
\DeclareBoolOption[false]{opsional}      % sertakan seluruh subbab opsional ("bila ada")
\DeclareBoolOption[false]{namalogo}      % cetak "Universitas Negeri Semarang" di bawah logo;
                                         % bawaan false karena logo bawaan sudah memuatnya

\ProcessKeyvalOptions*

% Boolean @-free yang bisa diubah pengguna di preamble (\unnescatatanfalse, \unnesopsionaltrue).
\newif\ifunnescatatan \newif\ifunnesopsional \newif\ifunnesnamalogo
\ifunnes@catatan \unnescatatantrue\else\unnescatatanfalse\fi
\ifunnes@opsional \unnesopsionaltrue\else\unnesopsionalfalse\fi
\ifunnes@namalogo \unnesnamalogotrue\else\unnesnamalogofalse\fi

%============================================================== validasi opsi
\newcommand{\unnes@galatopsi}[3]{%
  \ClassError{unnes-ta}{Nilai opsi #1 tidak dikenal: "#2"}{Pilihan yang tersedia: #3.}%
}
\newcommand{\unnes@cekopsi}[3]{%
  \@ifundefined{unnes@nilai@#1@#2}{\unnes@galatopsi{#1}{#2}{#3}}{}%
}
\@namedef{unnes@nilai@jenis@skripsi}{}\@namedef{unnes@nilai@jenis@proyek}{}
\@namedef{unnes@nilai@jenis@prototipe}{}\@namedef{unnes@nilai@jenis@publikasi}{}
\@namedef{unnes@nilai@jenis@prestasi}{}
\@namedef{unnes@nilai@mode@proposal}{}\@namedef{unnes@nilai@mode@laporan}{}
\@namedef{unnes@nilai@mode@repositori}{}
\@namedef{unnes@nilai@jenjang@sarjana}{}\@namedef{unnes@nilai@jenjang@diploma}{}
\@namedef{unnes@nilai@sitasi@apa}{}\@namedef{unnes@nilai@sitasi@ieee}{}
\@namedef{unnes@nilai@sitasi@mla}{}\@namedef{unnes@nilai@sitasi@chicago}{}
\@namedef{unnes@nilai@sitasi@harvard}{}\@namedef{unnes@nilai@sitasi@acs}{}
\@namedef{unnes@nilai@bahasa@id}{}\@namedef{unnes@nilai@bahasa@en}{}
\@namedef{unnes@nilai@halaman@bawah}{}\@namedef{unnes@nilai@halaman@atas}{}

\unnes@cekopsi{jenis}{\unnes@jenis}{skripsi, proyek, prototipe, publikasi, prestasi}
\unnes@cekopsi{mode}{\unnes@mode}{proposal, laporan, repositori}
\unnes@cekopsi{jenjang}{\unnes@jenjang}{sarjana, diploma}
\unnes@cekopsi{sitasi}{\unnes@sitasi}{apa, ieee, mla, chicago, harvard, acs}
\unnes@cekopsi{bahasa}{\unnes@bahasa}{id, en}
\unnes@cekopsi{halaman}{\unnes@halaman}{bawah, atas}

% mode=repositori hanya bermakna untuk publikasi ilmiah (panduan hal. 59)
\ifdefstring{\unnes@mode}{repositori}{%
  \ifdefstring{\unnes@jenis}{publikasi}{}{%
    \ClassWarning{unnes-ta}{mode=repositori hanya dipakai untuk jenis=publikasi
      (laporan publikasi tanpa isi artikel). Mode lain diabaikan.}%
  }%
}{}

%==================================================== boolean praktis (paket format)
% Dipakai oleh unnes-ta-sampul/pengesahan/awal/lampiran/sistematika/sitasi.
\newif\ifunnesproposal    \newif\ifunneslaporan   \newif\ifunnesrepositori
\newif\ifunnesdiploma     \newif\ifunnesindonesia
\AtBeginDocument{%
  \ifdefstring{\unnes@mode}{proposal}{\unnesproposaltrue}{\unnesproposalfalse}%
  \ifdefstring{\unnes@mode}{laporan}{\unneslaporantrue}{\unneslaporanfalse}%
  \ifdefstring{\unnes@mode}{repositori}{\unnesrepositoritrue}{\unnesrepositorifalse}%
  \ifdefstring{\unnes@jenjang}{diploma}{\unnesdiplomatrue}{\unnesdiplomafalse}%
  \ifdefstring{\unnes@bahasa}{id}{\unnesindonesiatrue}{\unnesindonesiafalse}%
}

%================================================================ kelas dasar
\ifunnes@draft  \PassOptionsToClass{draft}{report}\fi
\ifunnes@duasisi\PassOptionsToClass{twoside}{report}\else\PassOptionsToClass{oneside}{report}\fi
\LoadClass[12pt]{report}

%======================================================= gaya sitasi -> natbib
% Panduan hal. 91-92: gaya sitasi tidak ditetapkan; fakultas/prodi memilih di antara APA, IEEE,
% MLA, Chicago, Harvard, atau ACS. biber/biblatex tidak tersedia di TeX Live ini, jadi dipakai
% natbib + bibtex. natbib dimuat oleh unnes-ta-sitasi (lihat paket tersebut) supaya tabel preset
% gaya ada di satu tempat.

%===================================================================== paket
% Urutan ini penting: paket sitasi (memuat natbib lebih dulu), paket format, lalu hyperref paling akhir.
\RequirePackage{unnes-ta-sitasi}        % natbib + preset gaya sitasi & daftar pustaka
\RequirePackage{unnes-ta-core}          % halaman, font, spasi, nomor halaman
\RequirePackage{unnes-ta-identitas}     % metadata (judul, nama, prodi, pembimbing, penguji)
\RequirePackage{unnes-ta-bab}           % judul bab/subbab + nama bagian berbahasa Indonesia
\RequirePackage{unnes-ta-tabel-gambar}  % caption tabel/gambar, penomoran Bab.n
\RequirePackage{unnes-ta-sampul}        % sampul, halaman judul, punggung
\RequirePackage{unnes-ta-pengesahan}    % persetujuan, pengesahan penguji, pernyataan
\RequirePackage{unnes-ta-awal}          % moto, abstrak, prakata, daftar isi/gambar/tabel
\RequirePackage{unnes-ta-lampiran}      % lampiran + skeleton lampiran wajib
\RequirePackage{unnes-ta-sistematika}   % kerangka bab per jenis TA

\RequirePackage[hidelinks,bookmarksnumbered,bookmarksopen,plainpages=false]{hyperref}
% Metadata PDF diambil dari \identitas. Nilai harus diekspansi penuh dulu (\protected@edef),
% jika tidak hyperref mengeluh "Token not allowed in a PDF string" untuk \ifdefstring di \unneslabelta.
\AtBeginDocument{%
  \protected@edef\unnespdfjudul{\unnesjudul}%
  \protected@edef\unnespdfpenulis{\unnesnama}%
  \protected@edef\unnespdfsubjek{\unneslabelta{} -- \unnesprodi, \unnesfakultas, Universitas Negeri Semarang}%
  \hypersetup{%
    pdftitle  = {\unnespdfjudul},%
    pdfauthor = {\unnespdfpenulis},%
    pdfsubject= {\unnespdfsubjek}%
  }%
}

%=========================================================== ringkasan pilihan
\AtBeginDocument{%
  \PackageInfo{unnes-ta}{jenis=\unnes@jenis, mode=\unnes@mode, jenjang=\unnes@jenjang,%
    sitasi=\unnes@sitasi, bahasa=\unnes@bahasa, halaman=\unnes@halaman,
    logo=\unnes@logo, ukuranlogo=\unnes@ukuranlogo}%
}
\endinput
