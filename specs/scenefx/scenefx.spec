# ---------------------------------------------------------------------------
# Adapted from Fedora's rawhide dist-git scenefx.spec for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/scenefx/raw/rawhide/f/scenefx.spec
# Adapted 2026-09-24, with one real, deliberate deviation from upstream Fedora: Fedora's current
# scenefx spec is version 0.5, which requires pkgconfig(wlroots-0.20) - checked f44/f45/rawhide
# dist-git branches, ALL of them are pinned to wlroots-0.20 now, no 0.19-compatible version left
# in Fedora at all. `mangowm` (specs/mangowm/mangowm.spec, forked from Terra EL) needs
# pkgconfig(wlroots-0.19) specifically, and bumping to wlroots-0.20 would cascade into real version
# mismatches against el10's own base libraries (see specs/wlroots0.19/wlroots0.19.spec's header
# for the full list) - a materially bigger and riskier change than pinning scenefx itself down one
# version.
#
# Checked scenefx's own upstream release history (github.com/wlrfx/scenefx tags) for the last
# release that targeted wlroots-0.19: **0.4.1** (`meson.build`: `wlroots_version = ['>=0.19.0',
# '<0.20.0']`, `dependency('wlroots-0.19', ...)`). Downgraded this spec to that exact release,
# keeping Fedora's packaging structure/conventions (file layout, %files sections, subpackage
# naming) but with 0.4.1's actual (lower, less version-picky) own dependency floors from its
# meson.build: wayland-server >=1.23.1, libdrm >=2.4.122, pixman-1 >=0.43.0, xkbcommon (no pin) -
# all confirmed present/satisfiable on el10 in a full dependency sweep before writing this.
#
# Release/changelog: no %%autorelease/%%autochangelog to begin with (written directly for this
# repo, not machine-translated from an %%autorelease-using upstream spec).
#
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

Name:           scenefx
Version:        0.4.1
Release:        1%{?dist}
# scenefx's meson.build names its versioned library/pkgconfig/include-dir after MAJOR.MINOR only
# (`versioned_name = '@0@-@1@.@2@'.format(name, version_major, version_minor)`), not the full
# version - for Fedora's 0.5 those happen to be identical (no patch component), but our 0.4.1 has
# one, so this must NOT just be %%{version} in the %%files section below. Verified against 0.4.1's
# actual meson.build on GitHub before writing this, not assumed.
%global soname_ver 0.4
Summary:        A drop-in replacement for the wlroots scene API with eye-candy effects

License:        MIT
URL:            https://github.com/wlrfx/scenefx
Source0:        %{url}/archive/refs/tags/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wlroots-0.19) >= 0.19.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.122
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(lcms2)

%description
scenefx is a drop-in replacement for the wlroots scene API that allows
Wayland compositors to render surfaces with eye-candy effects -- including
blur, drop shadows, and rounded corners -- while keeping the simplicity of
the standard wlroots scene API. It is used by compositors such as SwayFX,
MangoWC, and mwc.

This build targets wlroots-0.19 (scenefx 0.4.1), not the current upstream
0.5/wlroots-0.20 pairing - see the header comment in this spec for why.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(wlroots-0.19)

%description devel
Header files and pkgconfig data needed to build Wayland compositors
against scenefx.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%meson -Dexamples=false
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libscenefx-%{soname_ver}.so

%files devel
%{_libdir}/pkgconfig/scenefx-%{soname_ver}.pc
%{_includedir}/scenefx-%{soname_ver}/

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.4.1-1
- Initial dank-ws-copr package: scenefx 0.4.1 (last release targeting wlroots-0.19),
  packaging structure adapted from Fedora's rawhide dist-git spec (currently at 0.5/wlroots-0.20)
