# ---------------------------------------------------------------------------
# Forked from Fedora rawhide (no epel9/epel10 branch exists - checked via
# src.fedoraproject.org branch HTTP status). Needed for `dms doctor`'s
# optional-feature check (cava powers DMS's audio-visualizer widget).
# Unmodified from Fedora's spec otherwise - all BuildRequires (alsa-lib-devel,
# fftw-devel, pulseaudio-libs-devel, libtool, ncurses-devel, iniparser-devel)
# are available directly from el10 BaseOS/AppStream/CRB, no forking needed
# for any of them.
# ---------------------------------------------------------------------------

Name:           cava
Version:        0.10.2
Release:        1%{?dist}
Summary:        Console-based Audio Visualizer for Alsa

License:        MIT
URL:            https://github.com/karlstav/cava
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  alsa-lib-devel
BuildRequires:  fftw-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  libtool
BuildRequires:  ncurses-devel
BuildRequires:  iniparser-devel
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  pkgconfig

%description
C.A.V.A. is a bar spectrum analyzer for audio using ALSA for input.

%prep
%autosetup -p1
./autogen.sh

%build
%configure FONT_DIR=/lib/kbd/consolefonts LIBS=-lrt
make %{?_smp_mflags} \
    cava_LDFLAGS=

%install
%make_install
rm -f %{buildroot}%{_libdir}/libiniparser.{a,la,so}

%files
%license LICENSE
%doc README.md
%doc example_files
%{_bindir}/cava
/lib/kbd/consolefonts/cava.psf

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.10.2-1
- Forked from Fedora rawhide for dank-ws-copr (no epel9/epel10 branch
  exists there); needed for dms doctor's cava check
