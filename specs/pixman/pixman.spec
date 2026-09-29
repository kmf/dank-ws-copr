# ---------------------------------------------------------------------------
# Forked from Fedora rawhide for dank-ws-copr. No epel9/epel10 branch exists
# there (checked via src.fedoraproject.org branch HTTP status) - el10's own
# pixman (0.43.4, from BaseOS) is too old for wlroots-0.20 (needs >=0.46.0),
# which mangowm 0.17.4 needs transitively. Bumped SYSTEM-WIDE (not a
# side-by-side compat package like wlroots0.19/wlroots0.20) because pixman's
# SONAME has stayed at libpixman-1.so.0 across this whole version range -
# confirmed directly (Fedora's own current 0.46.4 spec still ships the same
# `libpixman-1*.so.*` file pattern) - so existing binaries (cairo, mutter,
# weston, wlroots, hyprland/aquamarine/hyprtoolkit, niri, mir, qemu-kvm,
# Xwayland, etc. - checked via `dnf repoquery --whatrequires
# libpixman-1.so.0()(64bit)`) keep working unrebuilt, unlike the real
# SONAME-breaking conflicts documented for lua/iniparser elsewhere in this
# repo. %%check's %%meson_test dropped - needs a real display/GPU to render
# test cases, not appropriate for a headless mock/COPR chroot.
# ---------------------------------------------------------------------------

%define gitdate 20070827
%define gitrev 8ff7213f39edc1b2b8b60d6b0cc5d5f14ca1928d

Name:           pixman
Version:        0.46.4
Release:        1%{?dist}
Summary:        Pixel manipulation library

License:        MIT
URL:            https://gitlab.freedesktop.org/pixman/pixman
Source0:        https://xorg.freedesktop.org/archive/individual/lib/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  meson

%description
Pixman is a pixel manipulation library for X and Cairo.

%package devel
Summary: Pixel manipulation library development package
Requires: %{name}%{?isa} = %{version}-%{release}
Requires: pkgconfig

%description devel
Pixel manipulation library for X and Cairo development package.

%prep
%autosetup -p1

%build
%meson --auto-features=auto
%meson_build

%install
%meson_install

%ldconfig_post
%ldconfig_postun

%files
%doc COPYING
%{_libdir}/libpixman-1*.so.*

%files devel
%dir %{_includedir}/pixman-1
%{_includedir}/pixman-1/pixman.h
%{_includedir}/pixman-1/pixman-version.h
%{_libdir}/libpixman-1*.so
%{_libdir}/pkgconfig/pixman-1.pc

%changelog
* Tue Sep 29 2026 Karl Fischer <karl@obsidian.co.za> - 0.46.4-1
- Forked from Fedora rawhide for dank-ws-copr, bumped system-wide (same
  SONAME across this version range, confirmed via real reverse-dependency
  check); needed for wlroots-0.20 -> mangowm 0.17.4
