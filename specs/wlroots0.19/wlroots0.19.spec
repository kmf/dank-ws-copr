# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/wlroots0.19/raw/rawhide/f/wlroots0.19.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (checked: 404 on both) - unbranched, same
# pattern as every other fork this session. Needed as a compat/side-by-side package: el10's plain
# EPEL `wlroots` package is 0.18.2 (used by niri and others already installed), while `mangowm`
# needs the pkgconfig(wlroots-0.19) ABI specifically. Fedora's own naming convention
# (unversioned = current/latest ABI, `wlrootsX.Y` = older pinned ABI kept for compat) means this
# installs alongside plain `wlroots` without conflict - both ship differently-named
# `libwlroots-<ver>.so`/`wlroots-<ver>.pc` files.
#
# Deliberately NOT using Fedora's current unversioned `wlroots` (0.20.2): checked its BuildRequires
# against el10 and found real version mismatches (pixman-1 >=0.46.0 vs el10's 0.43.x,
# wayland-protocols >=1.47 vs el10's 1.41, xkbcommon >=1.8.0 vs el10's 1.7.0,
# libdisplay-info >=0.2.0 vs el10's 0.1.1) that would cascade into bumping multiple base system
# libraries - real risk of colliding with what niri and others already depend on. wlroots0.19's
# own (older, lower) version floors all matched el10's current versions cleanly with no bumps
# needed - confirmed via a full dependency sweep before forking.
#
# Changes vs. upstream Fedora spec: Release: %%autorelease -> plain 1%%{?dist};
# %%changelog: %%autochangelog -> manual entry (rpmautospec not available on el10).
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

# Version of the .so library
%global abi_ver 0.19
%global compat_ver %{abi_ver}
# libliftoff does not bump soname on API changes
%global liftoff_ver 0.5.0

Name:           wlroots%{compat_ver}
Version:        %{compat_ver}.3
Release:        1%{?dist}
Summary:        A modular Wayland compositor library

# Source files/overall project licensed as MIT, but
# - HPND-sell-variant
#   * protocol/drm.xml
#   * protocol/wlr-data-control-unstable-v1.xml
#   * protocol/wlr-foreign-toplevel-management-unstable-v1.xml
#   * protocol/wlr-gamma-control-unstable-v1.xml
#   * protocol/wlr-input-inhibitor-unstable-v1.xml
#   * protocol/wlr-layer-shell-unstable-v1.xml
#   * protocol/wlr-output-management-unstable-v1.xml
# - LGPL-2.1-or-later
#   * protocol/server-decoration.xml
# Those files are processed to C-compilable files by the
# `wayland-scanner` binary during build and don't alter
# the main license of the binaries linking with them by
# the underlying licenses.
License:        MIT
URL:            https://gitlab.freedesktop.org/wlroots/wlroots
Source0:        %{url}/-/releases/%{version}/downloads/wlroots-%{version}.tar.gz
Source1:        %{url}/-/releases/%{version}/downloads/wlroots-%{version}.tar.gz.sig
# 0FDE7BE0E88F5E48: emersion <contact@emersion.fr>
Source2:        https://emersion.fr/.well-known/openpgpkey/hu/dj3498u4hyyarh35rkjfnghbjxug6b19#/gpgkey-0FDE7BE0E88F5E48.gpg

# Upstream patches

# Fedora patches
# Following patch is required for phoc.
Patch:          Revert-layer-shell-error-on-0-dimension-without-anch.patch

BuildRequires:  gcc
BuildRequires:  glslang
BuildRequires:  gnupg2
BuildRequires:  meson >= 1.3

BuildRequires:  (pkgconfig(libliftoff) >= %{liftoff_ver} with pkgconfig(libliftoff) < 0.6)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm) >= 17.1.0
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm) >= 2.4.122
BuildRequires:  pkgconfig(libinput) >= 1.21.0
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
BuildRequires:  pkgconfig(vulkan) >= 1.2.182
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-errors)
BuildRequires:  pkgconfig(xcb-ewmh)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(xcb-renderutil)
BuildRequires:  pkgconfig(xcb-res)
BuildRequires:  pkgconfig(xcb-shm)
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-xinput)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xwayland)
# libliftoff does not bump soname on API changes
Requires:       libliftoff%{?_isa} >= %{liftoff_ver}

%description
%{summary}.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} == %{version}-%{release}
# not required per se, so not picked up automatically by RPM
Recommends:     pkgconfig(xcb-icccm)

%description    devel
Development files for %{name}.


%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup -N -n wlroots-%{version}
# apply unconditional patches (0..99)
%autopatch -p1 -M99
# apply conditional patches (100..)


%build
MESON_OPTIONS=(
    # Disable options requiring extra/unpackaged dependencies
    -Dexamples=false
)

%{meson} "${MESON_OPTIONS[@]}"
%{meson_build}


%install
%{meson_install}


%check
%{meson_test}


%files
%license LICENSE
%doc README.md
%{_libdir}/libwlroots-%{abi_ver}.so


%files  devel
%{_includedir}/wlroots-%{abi_ver}/wlr
%{_libdir}/pkgconfig/wlroots-%{abi_ver}.pc


%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.19.3-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
- Replaced %%autorelease/%%autochangelog (rpmautospec) with static Release/changelog
