# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's dist-git (src.fedoraproject.org/rpms/kitty,
# `epel10` branch, version 0.47.1), GPL-3.0-only AND more (see License: tag -
# Fedora spec files are conventionally reusable under the packaged software's
# own license per Fedora packaging norms, same as every other Fedora-sourced
# spec in this repo).
#
# Why this fork exists: EPEL10 already ships a working `kitty` (currently
# 0.47.1) - this isn't a packaging gap, just a couple of point releases
# behind upstream's latest (0.49.2, released 2026-10-01). This spec bumps to
# that latest version, since the user asked specifically for "the latest
# version of kitty" rather than EPEL's current one.
#
# Changes vs. Fedora's epel10 0.47.1 spec:
#   - Version bumped 0.47.1 -> 0.49.2.
#   - BuildRequires: golang >= 1.23.0 -> >= 1.26.0 (kitty's own go.mod now
#     requires go 1.26.0/toolchain go1.26.3 - checked directly, not assumed;
#     CentOS Stream 10 AppStream already ships golang 1.26.7, so no new repo
#     dependency).
#   - Source3 (kitty-vendor.tar.xz) regenerated for 0.49.2 via `go_vendor_archive
#     create --config go-vendor-tools.toml kitty-0.49.2/ -O kitty-vendor.tar.xz`
#     (go-vendor-tools is available directly in EPEL10, so this didn't need a
#     plain `go mod vendor` fallback - same real tool Fedora's own spec uses,
#     just run out-of-band since EPEL doesn't enable the Fedora-only
#     `%generate_buildrequires`/`%go_vendor_license_*` macros this spec's
#     `%if 0%{?fedora}` guards skip on EPEL anyway).
#   - New real build-time dependency in 0.49.x (not present in 0.47.1): the
#     "custom shaders" feature (added 0.49.0, packaging-fixed 0.49.1) needs
#     `slangc`, the shader-slang compiler (github.com/shader-slang/slang) to
#     generate shader pipeline variants at build time. Not packaged in
#     Fedora/EPEL at all, and building it from source would be its own large
#     side-project (a full multi-backend compiler toolchain). Upstream's own
#     `./dev.sh deps` build helper doesn't build it from source either - it
#     downloads shader-slang's official prebuilt release binary. Did the
#     same here: Source7/Source8 are shader-slang's own prebuilt
#     linux-x86_64/aarch64 release tarballs (glibc>=2.28 floor, el10 ships
#     2.39 - comfortably satisfied), extracted and pointed at via the
#     `SLANGC` env var (`kitty/constants.py`'s own documented override
#     mechanism) in %build, matching exactly how kitty's own build tooling
#     consumes it. `slangc` itself is a build-time-only tool - it generates
#     static shader program variants that get compiled into kitty's own
#     binary; it is never installed into the RPM or shipped to users.
#   - Otherwise no structural changes needed: `tools/cmd`'s Go kitten build
#     path, the Go module path, and every C pkgconfig BuildRequires are
#     unchanged between 0.47.1 and 0.49.2 (checked against CentOS Stream 10's
#     actual available versions, not assumed - harfbuzz-devel 8.4.0, wayland-
#     protocols-devel 1.41, pkgconfig(libxxhash) 0.8.4, simde-static 0.8.2,
#     cairo-devel, wayland-devel, lcms2-devel, ncurses, python3-devel 3.12 all
#     present and resolve).
# ---------------------------------------------------------------------------

%global gomodulesmode GO111MODULE=on
%global goipath kitty

%ifarch %{x86_64} %{arm64}
%bcond test 1
%else
%bcond test 0
%endif

Name:           kitty
Version:        0.49.2
Release:        1%{?dist}
Summary:        Cross-platform, fast, feature full, GPU based terminal emulator

# GPL-3.0-only: kitty
# Zlib: glfw
# LGPL-2.1-or-later: kitty/iqsort.h
# MIT: docs/_static/custom.css, shell-integration/ssh/bootstrap-utils.sh
# MIT AND CC0-1.0: simde
# CC0-1.0: 3rdparty/ringbuf
# BSD-2-Clause: 3rdparty/base64
# MIT: NerdFontsSymbolsOnly
# MIT: 3rdparty/verstable.h
License:        GPL-3.0-only AND LGPL-2.1-or-later AND Zlib AND (MIT AND CC0-1.0) AND BSD-2-Clause AND CC0-1.0 AND MIT
URL:            https://sw.kovidgoyal.net/kitty
Source0:        https://github.com/kovidgoyal/kitty/releases/download/v%{version}/%{name}-%{version}.tar.xz
Source1:        https://github.com/kovidgoyal/kitty/releases/download/v%{version}/%{name}-%{version}.tar.xz.sig
Source2:        https://calibre-ebook.com/signatures/kovid.gpg
# Generated out-of-band for this repo (go-vendor-tools is available directly
# in EPEL10 - see header comment):
#   go_vendor_archive create --config ./go-vendor-tools.toml ./kitty-%{version} -O kitty-vendor.tar.xz
Source3:        kitty-vendor.tar.xz
Source4:        go-vendor-tools.toml
# Add AppData manifest file
# * https://github.com/kovidgoyal/kitty/pull/2088
Source5:        kitty.appdata.xml
Source6:        https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/NerdFontsSymbolsOnly.tar.xz
# Prebuilt shader-slang compiler (build-time tool only, never shipped in the
# RPM - see header comment for why this isn't built from source).
Source7:        https://github.com/shader-slang/slang/releases/download/v2026.19/slang-2026.19-linux-x86_64-glibc-2.28.tar.gz
Source8:        https://github.com/shader-slang/slang/releases/download/v2026.19/slang-2026.19-linux-aarch64-glibc-2.28.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  golang >= 1.26.0
BuildRequires:  go-rpm-macros

BuildRequires:  gnupg2
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  lcms2-devel
BuildRequires:  libappstream-glib
BuildRequires:  ncurses
BuildRequires:  python3-devel >= 3.8
BuildRequires:  wayland-devel
BuildRequires:  simde-static

BuildRequires:  pkgconfig(cairo-fc)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(harfbuzz) >= 2.2
BuildRequires:  pkgconfig(libcanberra)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libxxhash)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xi)
BuildRequires:  pkgconfig(xinerama)
BuildRequires:  pkgconfig(xkbcommon-x11)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libcrypto)

%if %{with test}
# For tests:
BuildRequires:  fish
BuildRequires:  glibc-common
BuildRequires:  openssh-clients
BuildRequires:  ripgrep
BuildRequires:  zsh
BuildRequires:  python3dist(pillow)
%endif

Requires:       python3%{?_isa}
Requires:       hicolor-icon-theme

Obsoletes:      %{name}-bash-integration < 0.28.1-3
Obsoletes:      %{name}-fish-integration < 0.28.1-3
Provides:       %{name}-bash-integration = %{version}-%{release}
Provides:       %{name}-fish-integration = %{version}-%{release}

# Terminfo file has been split from the main program and is required for use
# without errors. It has been separated to support SSH into remote machines using
# kitty as per the maintainers suggestion. Install the terminfo file on the remote
# machine.
Requires:       %{name}-terminfo = %{version}-%{release}
Requires:       %{name}-shell-integration = %{version}-%{release}
Requires:       %{name}-kitten%{?_isa} = %{version}-%{release}

# For the "Hyperlinked grep" feature
Recommends:     ripgrep

# Very weak dependencies, these are required to enable all features of kitty's
# "kittens" functions install separately
Suggests:       ImageMagick%{?_isa}

Provides:       bundled(font(SymbolsNerdFontMono)) = 3.4.0
Provides:       bundled(font(SymbolsNerdFont)) = 3.4.0

Provides:       bundled(Verstable) = 2.1.1
# modified version of https://github.com/dhess/c-ringbuf
Provides:       bundled(c-ringbuf)
# heavily modified
Provides:       bundled(glfw)
# https://github.com/aklomp/base64
Provides:       bundled(base64simd)

%description
- Offloads rendering to the GPU for lower system load and buttery smooth
  scrolling. Uses threaded rendering to minimize input latency.

- Supports all modern terminal features: graphics (images), unicode, true-color,
  OpenType ligatures, mouse protocol, focus tracking, bracketed paste and
  several new terminal protocol extensions.

- Supports tiling multiple terminal windows side by side in different layouts
  without needing to use an extra program like tmux.

- Can be controlled from scripts or the shell prompt, even over SSH.

- Has a framework for Kittens, small terminal programs that can be used to
  extend kitty's functionality. For example, they are used for Unicode input,
  Hints and Side-by-side diff.

- Supports startup sessions which allow you to specify the window/tab layout,
  working directories and programs to run on startup.

- Cross-platform: kitty works on Linux and macOS, but because it uses only
  OpenGL for rendering, it should be trivial to port to other Unix-like
  platforms.

- Allows you to open the scrollback buffer in a separate window using arbitrary
  programs of your choice. This is useful for browsing the history comfortably
  in a pager or editor.

- Has multiple copy/paste buffers, like vim.


# terminfo package
%package        terminfo
Summary:        The terminfo file for Kitty Terminal
License:        GPL-3.0-only
BuildArch:      noarch

Requires:       ncurses-base

%description    terminfo
Cross-platform, fast, feature full, GPU based terminal emulator.

The terminfo file for Kitty Terminal.

# shell-integration package
%package        shell-integration
Summary:        Shell integration scripts for %{name}
License:        GPL-3.0-only AND MIT
BuildArch:      noarch

Recommends:     %{name}-kitten

%description    shell-integration
%{summary}.

# kitten package
%package        kitten
Summary:        The kitten executable
License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND GPL-3.0-only AND MIT AND OFL-1.1

%description    kitten
%{summary}.

%package        doc
Summary:        Documentation for %{name}
License:        GPL-3.0-only AND MIT
BuildArch:      noarch

BuildRequires:  python3dist(sphinx)

%description    doc
This package contains the documentation for %{name}.


%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup -p1 -a3

mkdir fonts
tar -xf %{SOURCE6} -C fonts

# Changing sphinx theme to classic
sed "s/html_theme = 'furo'/html_theme = 'classic'/" -i docs/conf.py

# Replace python shebangs to make them compatible with fedora
find -type f -name "*.py" -exec sed -e 's|/usr/bin/env python3|%{python3}|g'    \
                                    -e 's|/usr/bin/env python|%{python3}|g'     \
                                    -e 's|/usr/bin/env -S kitty|%{_bindir}/kitty|g' \
                                    -i "{}" \;

find -type f ! -executable -name "*.py" -exec sed -i '1{\@^#!%{python3}@d}' "{}" \;

%build
%set_build_flags

mkdir -p slangc-tool
%ifarch x86_64
tar -xzf %{SOURCE7} -C slangc-tool
%endif
%ifarch aarch64
tar -xzf %{SOURCE8} -C slangc-tool
%endif
export SLANGC="$(pwd)/slangc-tool/bin/slangc"
export LD_LIBRARY_PATH="$(pwd)/slangc-tool/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

%{python3} setup.py linux-package   \
    --libdir-name=%{_lib}           \
    --update-check-interval=0       \
    --verbose                       \
    --skip-building-kitten          \
    --ignore-compiler-warnings      \
    %{nil}

unset LDFLAGS
%gobuild -o _build/bin/kitten ./tools/cmd

%install
# rpmlint fixes
find linux-package/%{_lib}/%{name}/shell-integration -type f ! -executable -exec sed -r -i '1{\@^#!/bin/(fish|zsh|sh|bash)@d}' "{}" \;

cp -a linux-package/. %{buildroot}%{_prefix}
install -m0755 -Dp _build/bin/kitten %{buildroot}%{_bindir}/kitten

install -m0644 -Dp %{SOURCE5} %{buildroot}%{_metainfodir}/%{name}.appdata.xml

# rpmlint fixes
rm %{buildroot}%{_datadir}/doc/%{name}/html/.buildinfo \
   %{buildroot}%{_datadir}/doc/%{name}/html/.nojekyll


%check
%if %{with test}
export %{gomodulesmode}
# Some tests ignores PATH env...
mkdir -p kitty/launcher
ln -s %{buildroot}%{_bindir}/%{name} kitty/launcher/
# %%check runs in a fresh shell - SLANGC/LD_LIBRARY_PATH from %%build don't
# carry over, and kitty's own test_exe/test_slang_build tests re-check for
# slangc via shutil.which(), which needs it on PATH, not just $SLANGC.
export SLANGC="$(pwd)/slangc-tool/bin/slangc"
export LD_LIBRARY_PATH="$(pwd)/slangc-tool/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH=%{buildroot}%{_bindir}:$(pwd)/slangc-tool/bin:$PATH
export PYTHONPATH=$(pwd)
%{python3} setup.py test          \
    --prefix=%{buildroot}%{_prefix}
%endif

appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
desktop-file-validate %{buildroot}/%{_datadir}/applications/*.desktop


%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/*/*.{png,svg}
%{_libdir}/%{name}/
%exclude %{_libdir}/%{name}/shell-integration
%{_mandir}/man{1,5}/*.{1,5}*
%{_metainfodir}/*.xml

%files kitten
%license vendor/modules.txt
%license LICENSE
%{_bindir}/kitten

%files terminfo
%license LICENSE
%{_datadir}/terminfo/x/xterm-%{name}

%files shell-integration
%license LICENSE
%{_libdir}/%{name}/shell-integration/

%files doc
%license LICENSE
%doc CONTRIBUTING.md CHANGELOG.rst INSTALL.md
%{_docdir}/%{name}/html/
%dir %{_docdir}/%{name}


%changelog
* Fri Oct 02 2026 Karl Fischer <karl@obsidian.co.za> - 0.49.2-1
- Bump to latest upstream (0.49.2) - EPEL10 ships 0.47.1, user asked for
  latest. Regenerated the go-vendor-tools vendor archive for this version;
  bumped golang BuildRequires floor to >=1.26.0 to match kitty's own go.mod.
  No other structural changes needed - see header comment.
