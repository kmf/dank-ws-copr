# ---------------------------------------------------------------------------
# Written from scratch for dank-ws-copr - no distro spec exists anywhere
# (Fedora rawhide/epel9/epel10 all 404, checked via src.fedoraproject.org
# branch HTTP status). Needed by hyprland-guiutils (specs/hyprland-guiutils/),
# which needed by Hyprland's own polkit-agent/file-picker/crash-dialog
# fallbacks - the actual "missing hyprland-guiutils" gap this was forked to
# close. hyprland-qtutils (guiutils' Qt-based predecessor) is NOT what's
# needed here - guiutils dropped Qt entirely in favor of this, a native C++
# Wayland toolkit built directly on aquamarine/hyprutils/hyprlang/hyprgraphics
# (all already in this repo), so no Qt6/QML dependency at all.
#
# Same GCC14/libstdc++ completeness-gap pattern hit repeatedly this session
# (see specs/hyprland/, specs/hyprwire/, specs/mir/): this codebase's use of
# std::format with a std::vector<std::string> argument needs a range
# formatter specialization GCC 14's libstdc++ doesn't have - confirmed via
# a real failed build, fixed with gcc-toolset-16 (same one hyprland itself
# needed, for a different missing-symbol reason).
#
# Real build-time gap found and fixed separately: el10's own iniparser
# (4.1, from EPEL/BaseOS) never shipped a pkgconfig file at all - bumped to
# Fedora's current 4.2.6 in specs/iniparser/ (which does). See that spec's
# header for the narrow, documented conflict this creates with daxctl/ndctl/
# netatalk (all pin the old libiniparser.so.1) - accepted as low-risk for a
# desktop-shell-focused repo, same class of decision as the lua/wireplumber
# conflict documented in specs/lua/lua.spec.
# ---------------------------------------------------------------------------

Name:           hyprtoolkit
Version:        0.6.0
Release:        1%{?dist}
Summary:        A modern C++ Wayland-native GUI toolkit

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprtoolkit
Source0:        %{url}/archive/v%{version}/hyprtoolkit-%{version}.tar.gz
# Real upstream bug, still present on main as of 2026-09-25: PANGO_WRAP_NONE
# has never existed in any Pango release (checked el10's own pango-devel
# 1.54.0 headers directly - only WORD/CHAR/WORD_CHAR exist). Patches it to
# PANGO_WRAP_WORD_CHAR (same value used in the sibling branch); ellipsize
# already governs truncation in this code path so wrap mode barely matters.
Patch0:         0001-fix-invalid-PANGO_WRAP_NONE-symbol.patch

BuildRequires:  gcc-toolset-16-gcc-c++
BuildRequires:  gcc-toolset-16-gcc-plugin-annobin
BuildRequires:  cmake
BuildRequires:  pkgconfig
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(aquamarine) >= 0.10.0
BuildRequires:  pkgconfig(hyprgraphics) >= 0.3.0
BuildRequires:  pkgconfig(hyprutils) >= 0.14.2
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(iniparser)
BuildRequires:  pkgconfig(absl_flat_hash_map)

%description
hyprtoolkit is a modern, native C++ GUI toolkit for Wayland, built directly
on aquamarine/hyprutils/hyprlang/hyprgraphics. It backs the small GUI utility
apps in hyprland-guiutils (dialogs, the welcome screen, update/donate
prompts) used by Hyprland itself.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Header files and pkgconfig data needed to build applications using
hyprtoolkit (e.g. hyprland-guiutils).

%prep
%autosetup -p1 -n %{name}-%{version}

%build
# BUILD_TESTING defaults ON via CTest's own include() when built standalone
# (as we do here) - explicitly off to avoid a GTest BuildRequires for a
# from-scratch fork with no test-execution need.
source /usr/lib/gcc-toolset/16-env.source
%cmake -DBUILD_TESTING=OFF
%cmake_build

%install
source /usr/lib/gcc-toolset/16-env.source
%cmake_install

%files
%license LICENSE
%{_libdir}/libhyprtoolkit.so.*

%files devel
%{_includedir}/hyprtoolkit/
%{_libdir}/libhyprtoolkit.so
%{_libdir}/pkgconfig/hyprtoolkit.pc

%changelog
* Fri Sep 25 2026 Karl Fischer <karl@obsidian.co.za> - 0.6.0-1
- Initial dank-ws-copr package, written from scratch (no distro reference
  spec exists anywhere); needed by hyprland-guiutils
