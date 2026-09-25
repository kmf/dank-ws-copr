# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprwayland-scanner/raw/rawhide/f/hyprwayland-scanner.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (checked: 404 on both). Part of the Hyprland
# dependency chain toward eventually building `hyprland` itself (see SETUP.md and PLAN.md's
# hyprland blocker entry). Build-time-only tool, no runtime library deps beyond pugixml.
# Release: %%autorelease -> 1%%{?dist}; %%changelog: %%autochangelog -> manual (rpmautospec n/a on el10).
# UPDATE 2026-09-25: an earlier local bump to 0.4.6 (explored 2026-09-24 as a possible fix for an
# aquamarine 0.15.1 "zero-size array" build failure) was reverted back to 0.4.2 because it was never
# actually mock-built or confirmed necessary - aquamarine and hyprland only require
# hyprwayland-scanner-devel >= 0.4.0 and >= 0.3.10 respectively (checked their own upstream
# CMakeLists.txt directly), both satisfied by 0.4.2. This second bump to 0.4.6 (upstream's current
# latest tag) is unrelated to that abandoned fix attempt - it's a genuine, real, verified update
# (mock-built, installed, smoke-tested, and the full Hyprland chain rebuilt against it) rather than
# a repeat of the earlier untested claim.
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
* Fri Sep 25 2026 Karl Fischer <karl@obsidian.co.za> - 0.4.6-1
- Bump to upstream's current latest release, real mock build + install +
  smoke test this time (see spec header)

* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.4.2-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec
