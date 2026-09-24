# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprgraphics/raw/rawhide/f/hyprgraphics.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). Depends on hyprlang/hyprutils
# (above) and libspng (specs/libspng/, also forked - el10 had no pkgconfig(spng) provider at all).
# Kept the libjxl bcond disabled implicitly (no pkgconfig(libjxl*) checked/ported - not needed for
# hyprland itself, only an optional format).
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
#
# UPDATE 2026-09-24: bumped 0.1.5 -> 0.5.1 (`hyprland` requires hyprgraphics >=0.5.1, exact match).
# SOVERSION changed 0 -> 4 (checked upstream CMakeLists.txt at v0.5.1 directly), fixed the
# hardcoded `.so.0` in %%files accordingly. Real failed-build finding, fixed: 0.5.1's own deps
# changed too - added `mesa-libGLES-devel` (new `find_package(OpenGL COMPONENTS GLES3)` -
# confirmed missing via a real build failure: "Could NOT find OpenGL... GLES3"),
# `pkgconfig(pangocairo)`, `pkgconfig(librsvg-2.0)`; dropped `pkgconfig(spng)` (no longer used,
# replaced by `pkgconfig(libpng)` + librsvg) - all checked against 0.5.1's actual CMakeLists.txt,
# not assumed unchanged from 0.1.5.
# STATUS: 0.1.5 was mock-built successfully; this 0.5.1 bump not yet mock-built (first attempt hit
# the missing-GLES3 error above; retrying with the fix).
# ---------------------------------------------------------------------------

%bcond libjxl 0
Name:           hyprgraphics
Version:        0.5.1
Release:        1%{?dist}
Summary:        Graphics library for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprgraphics
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  mesa-libGLES-devel
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(librsvg-2.0)

%if %{with libjxl}
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_cms)
BuildRequires:  pkgconfig(libjxl_threads)
%endif

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.


%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%check
%ifarch s390x
rm tests/resource/images/hyprland.jpg
%endif
%ctest

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprgraphics.so.4
%{_libdir}/libhyprgraphics.so.%{version}

%files devel
%{_includedir}/hyprgraphics
%{_libdir}/libhyprgraphics.so
%{_libdir}/pkgconfig/hyprgraphics.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.1.5-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
- Disabled libjxl bcond (not needed for hyprland; avoids porting libjxl too)
