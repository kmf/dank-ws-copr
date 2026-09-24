# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/libspng/raw/rawhide/f/libspng.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). Only real missing dependency
# hyprgraphics needed (pkgconfig(spng) - everything else it needs was already on el10).
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

Name:           libspng
Version:        0.7.4
Release:        1%{?dist}
Summary:        Simple, modern libpng alternative

License:        BSD-2-Clause
URL:            https://libspng.org/
Source0:        https://github.com/randy408/libspng/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(zlib)

%description
Libspng is a C library for reading and writing Portable Network Graphics (PNG)
format files with a focus on security and ease of use.

Libspng is an alternative to libpng, the projects are separate and the APIs are
not compatible.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1
# NOTE: deliberately dropped Fedora's sed patch here (marking ch1n3p04/ch2n3p08 as should_fail to
# work around spng's incompatibility with libpng >=1.6.47's PNGv3 behavior change,
# https://github.com/randy408/libspng/issues/276) - el10's libpng is 1.6.40, predating that change,
# so applying the patch here caused the opposite problem: those two tests UNEXPECTEDLY PASS
# (meson/ctest treats an unexpected pass as a failure too), breaking %%check. Confirmed via a real
# failed mock build before removing this.

%build
%meson -Ddev_build=true
%meson_build

%install
%meson_install

%check
%meson_test

%files
%license LICENSE
%doc CONTRIBUTING.md README.md
%{_libdir}/libspng.so.0*

%files devel
%doc docs
%{_includedir}/spng.h
%{_libdir}/libspng.so
%{_libdir}/pkgconfig/spng.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.7.4-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
