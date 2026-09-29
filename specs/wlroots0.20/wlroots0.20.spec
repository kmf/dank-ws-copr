# ---------------------------------------------------------------------------
# Adapted from Fedora's own CURRENT unversioned `wlroots` dist-git spec
# (0.20.2 is Fedora's present-day "wlroots", not yet demoted to a "wlrootsX.Y"
# compat package there - checked src.fedoraproject.org/rpms/wlroots0.20:
# doesn't exist yet). Renamed here the same way Fedora itself names its own
# older-ABI compat packages (see specs/wlroots0.19/, forked from Fedora's real
# wlroots0.19 package) - `Name: wlroots0.20`, `abi_ver 0.20` - so it installs
# side-by-side with el10's plain `wlroots` (0.18.2, from EPEL, still used by
# `cage` - confirmed via `dnf repoquery --whatrequires wlroots`) rather than
# replacing it. Each wlroots minor version already ships a version-namespaced
# library/header/pkgconfig path (libwlroots-0.20.so, wlroots-0.20.pc, etc.) so
# there's no file collision either way - only the plain package NAME would
# collide, which this rename avoids.
#
# Needed for `mangowm` 0.17.4: its actual source (meson.build) requires
# wlroots-0.20 >=0.20.0 and pixman-1 - Terra's own packaged mangowm.spec is
# stale and still says wlroots-0.19 in BuildRequires, not matching what the
# source it packages actually needs (see specs/mangowm/mangowm.spec's own
# header for the corrected version).
#
# Version floor checked against el10 directly, one at a time: everything
# upstream's spec requires is already met on el10 (pixman-1 >=0.46.0 - bumped
# system-wide, see specs/pixman/; wayland-protocols >=1.47 - el10 has 1.49;
# xkbcommon >=1.8.0 - el10 has 1.13.1, already bumped for hyprland;
# wayland-server >=1.24.0 - el10 has 1.25.0; libdisplay-info >=0.2.0 - el10
# has exactly 0.2.0; gbm >=21.1 - el10 has 26.1.1; vulkan >=1.2.182 - el10 has
# 1.4.341.0; libliftoff >=0.5.0 <0.6 - el10 has 0.5.0) EXCEPT libdrm, which
# is short by one patch release (el10 has 2.4.128, upstream's spec pins
# >=2.4.129) - relaxed that one floor to >=2.4.128 rather than fork libdrm
# itself (a far more widely-depended-upon core graphics library than
# anything else in this chain); if the actual build needs a real 2.4.129 API,
# a real build failure will say so.
# ---------------------------------------------------------------------------

# Version of the .so library
%global abi_ver 0.20
%global compat_ver %{abi_ver}
# libliftoff does not bump soname on API changes
%global liftoff_ver 0.5.0

Name:           wlroots%{compat_ver}
Version:        %{compat_ver}.2
Release:        1%{?dist}
Summary:        A modular Wayland compositor library

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
BuildRequires:  pkgconfig(gbm) >= 21.1
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libdisplay-info) >= 0.2.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.128
BuildRequires:  pkgconfig(libinput) >= 1.21.0
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1) >= 0.46.0
BuildRequires:  pkgconfig(vulkan) >= 1.2.182
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.47
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.24.0
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
BuildRequires:  pkgconfig(xcb-xfixes) >= 1.15
BuildRequires:  pkgconfig(xcb-xinput)
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
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
* Tue Sep 29 2026 Karl Fischer <karl@obsidian.co.za> - 0.20.2-1
- Initial dank-ws-copr package, adapted from Fedora's current unversioned
  wlroots dist-git spec (renamed to wlroots0.20 for side-by-side install with
  el10's plain wlroots 0.18.2, same pattern as specs/wlroots0.19/); needed
  for mangowm 0.17.4
