# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprlang/raw/rawhide/f/hyprlang.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). Depends on hyprutils (above).
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
#
# UPDATE 2026-09-24: bumped BuildRequires hyprutils floor implicitly satisfied by the hyprutils
# 0.14.2 bump (specs/hyprutils/); hyprlang itself stays at Fedora's 0.6.4 version - wait, actually
# also bumped 0.6.4 -> 0.6.8 (`hyprland` requires hyprlang >=0.6.7). SOVERSION unchanged (still 2 at
# v0.6.8, checked upstream CMakeLists.txt directly), so %%files needed no soname fix here, unlike
# hyprutils/hyprgraphics.
# STATUS: 0.6.4 was mock-built successfully; this 0.6.8 bump not yet mock-built.
# ---------------------------------------------------------------------------

Name:           hyprlang
Version:        0.6.8
Release:        1%{?dist}
Summary:        The official implementation library for the hypr config language

License:        LGPL-3.0-only
URL:            https://github.com/hyprwm/hyprlang
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprutils) >= 0.7.1

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
%ctest

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprlang.so.2
%{_libdir}/libhyprlang.so.0.*

%files devel
%{_includedir}/hyprlang.hpp
%{_libdir}/libhyprlang.so
%{_libdir}/pkgconfig/hyprlang.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.6.4-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
