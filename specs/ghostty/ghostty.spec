# ---------------------------------------------------------------------------
# Forked/adapted from Terra EL (terrapkg/packages-el, branch `el10`, GPL-3.0):
#   https://github.com/terrapkg/packages-el/blob/el10/anda/devs/ghostty/stable/ghostty.spec
# Adapted for dank-ws-copr (plain COPR build, no Anda build system) on 2026-09-24.
#
# Changes vs. upstream Terra spec:
#   - BuildRequires: anda-srpm-macros removed (Anda-specific SRPM tooling, not needed/available
#     outside Terra's own build system; the minisign verification it would otherwise support is
#     already done explicitly in %%prep below).
#   - BuildRequires: zig0.15 -> zig (Terra versions Zig as separate `zigN.NN` packages; plain
#     EPEL10 ships a single current `zig` package, currently 0.15.2, which satisfies this).
#   - %%install rewritten to use the official `zig-rpm-macros` %%zig_install macro (defined by the
#     EPEL10 zig-rpm-macros package) instead of Terra/Anda's custom `%%{zig_build_target}` macro,
#     which does not exist outside Anda. Release-mode and extra build flags are set via
#     `_zig_release_mode` / `zig_install_options` overrides to match Terra's original invocation
#     as closely as possible.
#
# STATUS: NOT YET BUILT/TESTED. gtk4-layer-shell (pkgconfig(gtk4-layer-shell-0)) is required and
# does not exist anywhere in our enabled el10 repos — see SETUP.md Step 9. This spec will not
# build until that dependency is packaged first. Needs a mock build to validate the %%install
# macro translation above once that's in place.
# ---------------------------------------------------------------------------

# Signing key from https://github.com/ghostty-org/ghostty/blob/main/PACKAGING.md
%global public_key RWQlAjJC23149WL2sEpT/l0QKy7hMIFhYdQOFy0Z7z7PbneUgvlsnYcV
%global appid com.mitchellh.ghostty

Name:           ghostty
Version:        1.3.1
Release:        3%{?dist}
Summary:        A fast, native terminal emulator written in Zig.
License:        MIT AND MPL-2.0 AND OFL-1.1 AND (WTFPL OR CC0-1.0) AND Apache-2.0
URL:            https://ghostty.org/
Source0:        https://release.files.ghostty.org/%{version}/ghostty-%{version}.tar.gz
Source1:        https://release.files.ghostty.org/%{version}/ghostty-%{version}.tar.gz.minisig
# Vendored Zig package cache — see SETUP.md Step 10 for exactly how this was generated
# (`zig fetch` against every URL in build.zig.zon.txt, run with real network access outside the
# sandboxed mock/COPR build, then the resulting cache's `p/` dir tarred up). Needed because
# mock/COPR builds disable network during %%build/%%prep by design, but ghostty's upstream
# `nix/build-support/fetch-zig-cache.sh` fetches its Zig dependencies (incl. one git dependency)
# over the network at that point. Not hosted anywhere yet — currently a local file only
# (/tmp/ghostty-1.3.1-zig-vendor.tar.zst on durin); needs to be uploaded to actual COPR source
# storage (or regenerated in CI) before this spec can build outside this one mock test.
Source2:        ghostty-%{version}-zig-vendor.tar.zst
BuildRequires:  gettext
BuildRequires:  gtk4-devel
BuildRequires:  libadwaita-devel
BuildRequires:  libX11-devel
BuildRequires:  minisign
BuildRequires:  ncurses
BuildRequires:  ncurses-devel
BuildRequires:  pandoc-cli
BuildRequires:  systemd-rpm-macros
BuildRequires:  zig
BuildRequires:  zig-rpm-macros
BuildRequires:  zstd
BuildRequires:  pkgconfig(blueprint-compiler)
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(oniguruma)
BuildRequires:  pkgconfig(zlib)
Requires:       %{name}-terminfo = %{evr}
Requires:       (%{name}-kio = %{evr} if kf5-kio-core)
Requires:       (%{name}-kio = %{evr} if kf6-kio-core)
Requires:       gtk4
Requires:       gtk4-layer-shell
Requires:       libadwaita
Conflicts:      ghostty-nightly
Packager:       Gilver E. <roachy@fyralabs.com>

%description
👻 Ghostty is a fast, feature-rich, and cross-platform terminal emulator that uses platform-native UI and GPU acceleration.

%package        bash-completion
Summary:        Ghostty Bash completion
Requires:       %{name}
Requires:       bash-completion
Supplements:    (%{name} and bash-completion)
BuildArch:      noarch

%description    bash-completion
Bash shell completion for Ghostty.

%package        fish-completion
Summary:        Ghostty Fish completion
Requires:       %{name}
Requires:       fish
Supplements:    (%{name} and fish)
BuildArch:      noarch

%description    fish-completion
Fish shell completion for Ghostty.

%package        zsh-completion
Summary:        Ghostty Zsh completion
Requires:       %{name}
Requires:       zsh
Supplements:    (%{name} and zsh)
BuildArch:      noarch

%description    zsh-completion
Zsh shell completion for Ghostty.

%package        devel
Summary:        Development files for Ghostty.
Requires:       %{name} = %{evr}

%description    devel
This package includes the development files for Ghostty.

%package        kio
Summary:        KIO support for Ghostty
Requires:       %{name} = %{evr}
BuildArch:      noarch

%description    kio
This package allows Ghostty to interact with KIO.

%package        nautilus
Summary:        Nautilus menu support for Ghostty
Supplements:    (%{name} and nautilus)
Requires:       %{name} = %{evr}
Requires:       nautilus-python
BuildArch:      noarch

%description    nautilus
This package enables Nautilus integration for Ghostty.

%package        vim
Summary:        Vim plugins for Ghostty
Supplements:    (%{name} and vim-filesystem)
Requires:       %{name} = %{evr}
Requires:       vim-enhanced
Requires:       vim-filesystem
BuildArch:      noarch

%description    vim
This package provides the Ghostty Vim plugins.

%package        neovim
Summary:        Neovim plugins for Ghostty
Supplements:    (%{name} and neovim)
Requires:       %{name} = %{evr}
Requires:       neovim
BuildArch:      noarch

%description    neovim
This package provides the Neovim plugins for Ghostty.

%package        bat-syntax
Summary:        Bat syntax for Ghostty
Supplements:    (%{name} and bat)
Requires:       %{name} = %{evr}
Requires:       bat
BuildArch:      noarch

%description    bat-syntax
This package provides the Bat syntax files for Ghostty.

%package        shell-integration
Summary:        Ghostty shell integration
Supplements:    %{name}
BuildArch:      noarch

%description    shell-integration
This package contains files allowing Ghostty to integrate with various shells.

%package        terminfo
Summary:        Ghostty terminfo
%if 0%{?fedora} >= 42
Requires:       ncurses-term >= 6.5-5.20250125
%endif
Supplements:    %{name}
Obsoletes:      %{name}-terminfo-source < %{evr}
BuildArch:      noarch

%description    terminfo
Ghostty's terminfo. Needed for basic terminal function.

%package -n     libghostty-vt
Summary:        The libghostty-vt libraries

%description -n libghostty-vt
This package contains the libghostty-vt libraries, the first of many libghostty libaries in development.

%package -n     libghostty-vt-devel
Summary:        Development files for libghostty-vt
Requires:       libghostty-vt = %{evr}

%description -n libghostty-vt-devel
This package contains the libraries and header files that are needed for developing with libghostty-vt.

%prep
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -P %{public_key}
%autosetup

# Replaces upstream's `ZIG_GLOBAL_CACHE_DIR=... ./nix/build-support/fetch-zig-cache.sh`, which
# requires network access unavailable in a mock/COPR build (see Source2 comment above).
# NOTE: unlike Terra's original (which used their own Anda-specific `%%{zig_build_target}` macro
# and renamed this dir to `zig-pkg` to match it), we leave it named `p` here — the official
# zig-rpm-macros `%%zig_install` macro (via `_zig_package_dir` = `_zig_cache_dir/p`) expects that
# exact name. Renaming it broke the build the first time this was tried (see SETUP.md Step 10).
mkdir -p "%{_zig_cache_dir}"
tar --zstd -xf %{SOURCE2} -C "%{_zig_cache_dir}"

%build

%install
# Translated from Terra's `%{zig_build_target -r fast} ...` (Anda-specific macro) to the
# official zig-rpm-macros `%zig_install`, which already applies --prefix/--prefix-lib-dir/
# --prefix-exe-dir/--prefix-include-dir from `_zig_install_options` (see macros.zig). "-r fast"
# maps to overriding `_zig_release_mode`; the rest map to `zig_install_options`.
%global _zig_release_mode fast
%global zig_install_options -Dversion-string="%{version}" -Dstrip=false -Dpie=true -Demit-docs -Demit-themes=false
# el10's harfbuzz-devel (8.4.0) is too old for ghostty's bindings, which expect the newer
# harfbuzz it vendors itself (11.0.0, fetched into the Source2 vendor cache above) - discovered
# via a real build failure (`error: ... has no member named 'HB_BUFFER_CLUSTER_LEVEL_GRAPHEMES'`,
# see SETUP.md Step 10). `-fno-sys=<name>` is Zig's build-runner flag (see
# /usr/lib/zig/compiler/build_runner.zig) to force building the vendored copy of a dependency
# instead of linking the system one ghostty's build.zig would otherwise prefer by default.
%global zig_build_options -fno-sys=harfbuzz
%zig_install

# Don't conflict with ncurses-term on F42 and up
%if 0%{?fedora} >= 42
rm -rf %{buildroot}%{_datadir}/terminfo/g/%{name}
%endif

%find_lang %{appid}

%files -f %{appid}.lang
%doc README.md
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/%{name}/doc/
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/dbus-1/services/%{appid}.service
%{_iconsdir}/hicolor/16x16/apps/%{appid}.png
%{_iconsdir}/hicolor/16x16@2/apps/%{appid}.png
%{_iconsdir}/hicolor/32x32/apps/%{appid}.png
%{_iconsdir}/hicolor/32x32@2/apps/%{appid}.png
%{_iconsdir}/hicolor/128x128/apps/%{appid}.png
%{_iconsdir}/hicolor/128x128@2/apps/%{appid}.png
%{_iconsdir}/hicolor/256x256/apps/%{appid}.png
%{_iconsdir}/hicolor/256x256@2/apps/%{appid}.png
%{_iconsdir}/hicolor/512x512/apps/%{appid}.png
%{_iconsdir}/hicolor/1024x1024/apps/%{appid}.png
%{_mandir}/man1/%{name}.1.gz
%{_mandir}/man5/%{name}.5.gz
%{_userunitdir}/app-%{appid}.service

%files bash-completion
%{bash_completions_dir}/%{name}.bash

%files fish-completion
%{fish_completions_dir}/%{name}.fish

%files zsh-completion
%{zsh_completions_dir}/_%{name}

%files devel
%{_includedir}/ghostty/

%files kio
%{_datadir}/kio/servicemenus/%{appid}.desktop

%files nautilus
%{_datadir}/nautilus-python/extensions/%{name}.py

%files vim
%{_datadir}/vim/vimfiles/compiler/%{name}.vim
%{_datadir}/vim/vimfiles/ftdetect/%{name}.vim
%{_datadir}/vim/vimfiles/ftplugin/%{name}.vim
%{_datadir}/vim/vimfiles/syntax/%{name}.vim

%files neovim
%{_datadir}/nvim/site/compiler/%{name}.vim
%{_datadir}/nvim/site/ftdetect/%{name}.vim
%{_datadir}/nvim/site/ftplugin/%{name}.vim
%{_datadir}/nvim/site/syntax/%{name}.vim

%files bat-syntax
%{_datadir}/bat/syntaxes/%{name}.sublime-syntax

%files shell-integration
%{_datadir}/%{name}/shell-integration/

%files terminfo
%if 0%{?fedora} < 42
%{_datadir}/terminfo/g/%{name}
%endif
%{_datadir}/terminfo/x/xterm-%{name}

%post
%systemd_user_post app-%{appid}.service

%preun
%systemd_user_preun app-%{appid}.service

%postun
%systemd_user_postun app-%{appid}.service

%files -n libghostty-vt
%{_libdir}/libghostty-vt.so.*

%files -n libghostty-vt-devel
%{_libdir}/libghostty-vt.so
%{_datadir}/pkgconfig/libghostty-vt.pc

%changelog
* Tue Oct 28 2025 Gilver E. <rockgrub@disroot.org> - 1.2.3-2
- Disabled bundled themes
 * This is necessary to address licensing issues in the themes repo Ghostty uses
 * See: https://github.com/mbadolato/iTerm2-Color-Schemes/issues/638
* Fri Jan 31 2025 Gilver E. <rockgrub@disroot.org>
- Update to 1.1.0-1
 * Low GHSA-98wc-794w-gjx3: Ghostty leaked file descriptors allowing the shell and any of its child processes to impact other Ghostty terminal instances
 * Ghostty terminfo source files are now a subpackage
 * Shell integration and completion and terminfo subpackages are now properly noarch
* Tue Dec 31 2024 Gilver E. <rockgrub@disroot.org>
- Update to 1.0.1
 * High CVE-2003-0063: Allows execution of arbitrary commands
 * Medium CVE-2003-0070: Allows execution of arbitrary commands

* Thu Dec 26 2024 Gilver E. <rockgrub@disroot.org>
- Initial package
