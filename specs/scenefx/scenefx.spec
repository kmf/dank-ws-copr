# ---------------------------------------------------------------------------
# Adapted from Fedora's rawhide dist-git scenefx.spec for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/scenefx/raw/rawhide/f/scenefx.spec
#
# UPDATE 2026-09-29: bumped BACK to Fedora's current 0.5 (wlroots-0.20),
# superseding the 2026-09-24 decision (see git history) to pin this at 0.4.1
# for wlroots-0.19. That decision was made because mangowm's own packaged
# spec (Terra's) declared `pkgconfig(wlroots-0.19)` - but checking mango
# 0.17.4's actual source (meson.build) directly showed Terra's spec is
# stale/wrong: mango really needs wlroots-0.20 (`dependency('wlroots-0.20',
# version: '>=0.20.0')`), same as scenefx 0.5 itself. specs/wlroots0.20/ was
# forked to provide that (side-by-side with el10's plain 0.18.2 wlroots, same
# pattern as specs/wlroots0.19/). Nothing else in this repo depended on the
# 0.4.1 build (confirmed via `rpm -q --whatrequires scenefx` before
# replacing it), so this is a clean in-place bump, not a side-by-side
# situation - only one `scenefx` package can exist at a time either way,
# since (unlike wlroots) Fedora doesn't namespace scenefx's package NAME by
# ABI version, only its library/pkgconfig/include paths.
# ---------------------------------------------------------------------------

Name:           scenefx
Version:        0.5
Release:        1%{?dist}
Summary:        A drop-in replacement for the wlroots scene API with eye-candy effects

License:        MIT
URL:            https://github.com/wlrfx/scenefx
Source0:        %{url}/archive/refs/tags/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  pkgconfig(wayland-server) >= 1.24.0
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.128
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
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

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(wlroots-0.20)

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
%{_libdir}/libscenefx-%{version}.so

%files devel
%{_libdir}/pkgconfig/scenefx-%{version}.pc
%{_includedir}/scenefx-%{version}/

%changelog
* Tue Sep 29 2026 Karl Fischer <karl@obsidian.co.za> - 0.5-1
- Bumped back to Fedora's current 0.5/wlroots-0.20 - see header comment.
  Needed for real (corrected) mangowm 0.17.4 dependency floors.

* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.4.1-1
- Initial dank-ws-copr package: scenefx 0.4.1 (last release targeting wlroots-0.19),
  packaging structure adapted from Fedora's rawhide dist-git spec (currently at 0.5/wlroots-0.20)
