# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprgraphics/raw/rawhide/f/hyprgraphics.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). Depends on hyprlang/hyprutils
# (above) and libspng (specs/libspng/, also forked - el10 had no pkgconfig(spng) provider at all).
# Kept the libjxl bcond disabled implicitly (no pkgconfig(libjxl*) checked/ported - not needed for
# hyprland itself, only an optional format).
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

%bcond libjxl 0
Name:           hyprgraphics
Version:        0.1.5
Release:        1%{?dist}
Summary:        Graphics library for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprgraphics
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(spng)

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
%{_libdir}/libhyprgraphics.so.0
%{_libdir}/libhyprgraphics.so.%{version}

%files devel
%{_includedir}/hyprgraphics
%{_libdir}/libhyprgraphics.so
%{_libdir}/pkgconfig/hyprgraphics.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.1.5-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
- Disabled libjxl bcond (not needed for hyprland; avoids porting libjxl too)
