# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprwayland-scanner/raw/rawhide/f/hyprwayland-scanner.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (checked: 404 on both). Part of the Hyprland
# dependency chain toward eventually building `hyprland` itself (see SETUP.md and PLAN.md's
# hyprland blocker entry). Build-time-only tool, no runtime library deps beyond pugixml.
# Release: %%autorelease -> 1%%{?dist}; %%changelog: %%autochangelog -> manual (rpmautospec n/a on el10).
# UPDATE 2026-09-24: bumped 0.4.2 -> 0.4.6 to test whether it fixes a real aquamarine 0.15.1 build
# failure ("zero-size array" compile errors in generated protocol .cpp files) - plausible
# hyprwayland-scanner code-gen bug fixed in a later release, not yet confirmed.
# STATUS: 0.4.2 was mock-built successfully; this 0.4.6 bump not yet mock-built.
# ---------------------------------------------------------------------------

Name:           hyprwayland-scanner
Version:        0.4.6
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
