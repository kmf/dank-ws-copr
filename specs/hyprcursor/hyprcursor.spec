# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprcursor/raw/rawhide/f/hyprcursor.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). Depends on hyprlang (above).
# Fedora's `Source: HyprBibataModernClassicSVG.tar.gz` (test-data for %%check) lives in Fedora's
# lookaside cache, not a plain public URL - resolved via
# https://src.fedoraproject.org/lookaside/pkgs/hyprcursor/HyprBibataModernClassicSVG.tar.gz/sha512/<hash>/HyprBibataModernClassicSVG.tar.gz
# (hash from Fedora's `sources` metadata file for this package) and vendored directly below.
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

Name:           hyprcursor
Version:        0.1.11
Release:        1%{?dist}
Summary:        The hyprland cursor format, library and utilities

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprcursor
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# test data - see header comment above for provenance
Source1:        HyprBibataModernClassicSVG.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++

BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libzip)
BuildRequires:  pkgconfig(tomlplusplus)

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.

%prep
%autosetup -p1 -a1
mkdir -p $HOME/.icons
mv HyprBibataModernClassicSVG $HOME/.icons

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
%{_bindir}/hyprcursor-util
%{_libdir}/lib%{name}.so.%{version}
%{_libdir}/lib%{name}.so.0

%files devel
%{_includedir}/%{name}.hpp
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.1.11-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
