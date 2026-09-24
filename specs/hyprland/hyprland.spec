# ---------------------------------------------------------------------------
# Written from scratch for dank-ws-copr - no Fedora, Terra, or any other distro spec exists for
# hyprland anywhere (checked exhaustively: Fedora rawhide/epel9/epel10 all 404; Terra deliberately
# removed their spec, "doesn't build anymore... whole freedesktop thing" - see SETUP.md Step 8).
# This is the capstone of the whole Hyprland dependency chain built up this session: aquamarine,
# hyprutils, hyprlang, hyprcursor, hyprgraphics, hyprwayland-scanner, hyprwire,
# hyprland-protocols, libxkbcommon (bumped), lua (bumped), muparser - all specs/ in this repo.
#
# Two upstream dependencies needed vendoring rather than packaging separately:
#   - glaze (header-only C++ JSON lib): hyprland's own CMakeLists.txt already handles "not found"
#     via FetchContent from GitHub - rather than fight that, vendored the exact tarball as Source1
#     and pointed FETCHCONTENT_SOURCE_DIR_GLAZE at the extracted copy in %%prep, so FetchContent
#     uses it locally instead of a network git clone (mock/COPR builds have no network in %%build).
#   - udis86 (x86 disassembler, only used by Hyprland's plugin-loading diagnostics): hyprland's
#     CMakeLists.txt falls back to `add_subdirectory(subprojects/udis86)` (a git submodule, not
#     included in GitHub's release tarball) if no system udis86 is found. Packaging Fedora's own
#     `udis86` separately looked possible but its pkgconfig-less `%%files` layout wouldn't satisfy
#     hyprland's `pkg_check_modules(udis86)` check anyway (falls through to `find_library`, which
#     *might* work, but untested) - simpler and more certain to vendor the EXACT submodule commit
#     hyprland pins (`canihavesomecoffee/udis86` @ 5336633, checked via GitHub's API against the
#     hyprwm/Hyprland tree at this tag) directly into subprojects/udis86/ in %%prep, matching
#     upstream's own fallback path exactly.
#
# Real, systemic toolchain finding (see specs/hyprwire/hyprwire.spec and specs/mir/mir.spec for the
# full pattern first discovered there): applied preemptively here rather than waiting to hit it -
# el10's default GCC 14.4.1 has real libstdc++ completeness gaps against recent C++ standard
# library features that this codebase (C++26!) almost certainly needs. Using `gcc-toolset-15`
# (official, opt-in newer-GCC package on el10) from the start, with the same
# `source .../15-env.source` + `gcc-toolset-15-gcc-plugin-annobin` pattern.
#
# hyprctl's own CMakeLists.txt (a subdirectory built as part of this same project) needed
# `hyprwire` (forked separately, specs/hyprwire/ - didn't exist anywhere either) and `re2`/
# `readline` (both already on el10). hyprland-protocols needed bumping past Fedora's stale version
# AND a Meson->CMake build-system rewrite (specs/hyprland-protocols/, see its own header).
#
# CMake 3.30+ and C++26 both confirmed to actually work on el10 (checked directly, see SETUP.md
# Step 15/hyprland's PLAN.md entry) - not the blockers they first appeared to be.
#
# KNOWN OPEN ISSUE, not yet resolved: `lua` (specs/lua/, bumped to 5.5.1 to satisfy hyprland's
# `lua>=5.5,<5.6` requirement) collides with el10's own built-in `lua-libs` 5.4, which
# `ibus-libpinyin`/`brlapi` depend on - see PLAN.md's hyprland entry. Not a build-time blocker
# (mock/COPR chroots don't have those packages installed), but a real install-time conflict for
# any real user who has them - needs a decision before this ships for real.
#
# STATUS: first draft, not yet mock-built. Given the pattern for every other package this session,
# expect real iteration even with every dependency present.
# ---------------------------------------------------------------------------

%global udis86_commit 5336633af70f3917760a6d441ff02d93477b0c86
%global glaze_version 7.2.0

Name:           hyprland
Version:        0.56.2
Release:        1%{?dist}
Summary:        A dynamic tiling Wayland compositor

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/Hyprland
Source0:        %{url}/archive/v%{version}/Hyprland-%{version}.tar.gz
Source1:        https://github.com/stephenberry/glaze/archive/v%{glaze_version}/glaze-%{glaze_version}.tar.gz
Source2:        https://github.com/canihavesomecoffee/udis86/archive/%{udis86_commit}/udis86-%{udis86_commit}.tar.gz

BuildRequires:  gcc-toolset-15-gcc-c++
BuildRequires:  gcc-toolset-15-gcc-plugin-annobin
BuildRequires:  cmake
BuildRequires:  git-core
BuildRequires:  python3
BuildRequires:  mesa-libGLES-devel
BuildRequires:  glslang-devel
BuildRequires:  pkgconfig(aquamarine) >= 0.9.3
BuildRequires:  pkgconfig(hyprlang) >= 0.6.7
BuildRequires:  pkgconfig(hyprcursor) >= 0.1.7
BuildRequires:  pkgconfig(hyprutils) >= 0.14.0
BuildRequires:  pkgconfig(hyprgraphics) >= 0.5.1
BuildRequires:  pkgconfig(hyprwire)
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.7.0
BuildRequires:  hyprwayland-scanner-devel >= 0.3.10
BuildRequires:  pkgconfig(xkbcommon) >= 1.11.0
BuildRequires:  pkgconfig(uuid)
BuildRequires:  pkgconfig(wayland-server) >= 1.22.91
BuildRequires:  pkgconfig(wayland-protocols) >= 1.49
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput) >= 1.29
BuildRequires:  pkgconfig(libeis-1.0)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(re2)
BuildRequires:  pkgconfig(muparser)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(lua) >= 5.5
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  readline-devel
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-res)
BuildRequires:  pkgconfig(xcb-errors)

Requires:       xdg-desktop-portal
Recommends:     xorg-x11-server-Xwayland

%description
Hyprland is a dynamic tiling Wayland compositor based on aquamarine, that
doesn't sacrifice on its looks. It provides the latest Wayland features,
is highly customizable, and has plenty of eyecandy features.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Header files needed to build plugins for Hyprland.

%prep
%autosetup -p1 -n Hyprland-%{version}
tar xf %{SOURCE1} -C ..
tar xf %{SOURCE2} -C .
mv ../glaze-%{glaze_version} ../hyprland-glaze-src
mkdir -p subprojects
mv udis86-%{udis86_commit} subprojects/udis86

%build
source /usr/lib/gcc-toolset/15-env.source
%cmake \
  -DNO_HYPRPM=OFF \
  -DFETCHCONTENT_SOURCE_DIR_GLAZE="%{_builddir}/hyprland-glaze-src" \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON
%cmake_build

%install
source /usr/lib/gcc-toolset/15-env.source
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/Hyprland
%{_bindir}/hyprland
%{_bindir}/hyprctl
%{_bindir}/hyprpm
%{_bindir}/start-hyprland
%{_datadir}/wayland-sessions/hyprland.desktop
%{_datadir}/hypr/
%{_datadir}/xdg-desktop-portal/hyprland-portals.conf
%{_datadir}/bash-completion/completions/hyprctl
%{_datadir}/fish/vendor_completions.d/hyprctl.fish
%{_datadir}/zsh/site-functions/_hyprctl
%{_mandir}/man1/*

%files devel
%{_includedir}/hyprland/
%{_datadir}/pkgconfig/hyprland.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.56.2-1
- Initial dank-ws-copr package, written from scratch (no distro reference spec exists anywhere)
