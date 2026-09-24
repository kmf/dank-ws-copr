# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/hyprland-protocols/raw/rawhide/f/hyprland-protocols.spec
# Adapted 2026-09-24. Not branched to epel9/epel10 (404 on both). One of hyprland's own optional
# deps: `pkg_check_modules(hyprland_protocols_dep hyprland-protocols>=0.7.0)` - if not found,
# hyprland falls back to its own `subprojects/hyprland-protocols` git submodule, which isn't
# present in GitHub's auto-generated release tarball (submodules aren't included). Packaging this
# properly avoids needing to vendor that submodule's content separately.
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
# Bumped 0.4.0 -> 0.7.1 up front (Fedora's rawhide version is below hyprland's own `>=0.7.0` floor
# in its CMakeLists.txt pkg_check_modules call) - checked and bumped immediately rather than
# hitting the same "stale Fedora version" surprise found repeatedly with hyprutils/hyprlang/
# hyprgraphics/scenefx earlier this session.
#
# Real second finding, from an actual failed build: 0.7.1 switched build systems entirely, Meson ->
# CMake (`ERROR: Neither source directory '.' nor build directory ... contain a build file
# meson.build`) - Fedora's spec (still on the old 0.4.0/Meson era) couldn't just be bumped in place.
# Rewrote %%build/%%install for %%cmake/%%cmake_build/%%cmake_install against 0.7.1's actual
# CMakeLists.txt (a trivial `LANGUAGES NONE` data-only project - just installs protocol XML files
# and a generated .pc file, no compilation).
# STATUS: not yet mock-built (first attempt hit the meson/cmake mismatch above).
# ---------------------------------------------------------------------------

Name:           hyprland-protocols
Version:        0.7.1
Release:        1%{?dist}
Summary:        Wayland protocol extensions for Hyprland
BuildArch:      noarch

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-protocols
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake

%description
%{summary}.

%package        devel
Summary:        Wayland protocol extensions for Hyprland

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
%{_datadir}/pkgconfig/%{name}.pc
%{_datadir}/%{name}/


%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.7.1-1
- Initial dank-ws-copr package, adapted from Fedora rawhide dist-git spec, bumped to 0.7.1
