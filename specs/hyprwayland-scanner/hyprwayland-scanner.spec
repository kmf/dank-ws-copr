# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprwayland-scanner/raw/rawhide/f/hyprwayland-scanner.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (checked: 404 on both). Part of the Hyprland
# dependency chain toward eventually building `hyprland` itself (see SETUP.md and PLAN.md's
# hyprland blocker entry). Build-time-only tool, no runtime library deps beyond pugixml.
# Release: %%autorelease -> 1%%{?dist}; %%changelog: %%autochangelog -> manual (rpmautospec n/a on el10).
# UPDATE 2026-09-25: reverted an unconfirmed local bump to 0.4.6 that was explored 2026-09-24 as a
# possible fix for an aquamarine 0.15.1 "zero-size array" build failure, but never actually
# mock-built or confirmed necessary (this file's own prior header said so explicitly) - aquamarine
# only requires hyprwayland-scanner-devel >= 0.4.0 (see specs/aquamarine/aquamarine.spec) and built
# successfully against 0.4.2, so the bump was never needed. Reverted to match what's actually built,
# installed, and live on the real kmf/dank-ws-copr COPR (build 11030603) - see TESTING.md.
# ---------------------------------------------------------------------------

Name:           hyprwayland-scanner
Version:        0.4.2
Release:        1%{?dist}
Summary:        A Hyprland implementation of wayland-scanner, in and for C++

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwayland-scanner
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  cmake(pugixml)
BuildRequires:  gcc-c++

%description
%{summary}.

%package        devel
Summary:        A Hyprland implementation of wayland-scanner, in and for C++

%description    devel
%{summary}.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/cmake/%{name}/

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.4.2-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
