# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprutils/raw/rawhide/f/hyprutils.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). Base utility lib used by nearly
# every other Hyprland-ecosystem package (hyprlang, hyprcursor, hyprgraphics, aquamarine, hyprland
# itself). Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

Name:           hyprutils
Version:        0.7.1
Release:        1%{?dist}
Summary:        Hyprland utilities library used across the ecosystem

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprutils
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(pixman-1)

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
%{_libdir}/lib%{name}.so.%{version}
%{_libdir}/lib%{name}.so.6

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.7.1-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
