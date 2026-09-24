# ---------------------------------------------------------------------------
# Written from scratch for dank-ws-copr - no Fedora, Terra, or any other distro spec exists for
# hyprwire anywhere (checked: Fedora rawhide/epel9/epel10 all 404). Needed because `hyprctl`
# (hyprland's own control-utility subdirectory, built as part of the same hyprland.spec) requires
# `pkgconfig(hyprwire)` - discovered while reading hyprland's own hyprctl/CMakeLists.txt before
# writing hyprland.spec itself, not from a failed build.
#
# Structured to match this repo's aquamarine/hyprwayland-scanner conventions (same hyprwm org, same
# CMake idioms - a top-level lib plus an internal `scanner` subdirectory building its own
# `hyprwire-scanner` tool, mirroring how aquamarine depends on the separate hyprwayland-scanner).
# Full dependency sweep against el10 before writing this: hyprutils>=0.9.0 (have 0.14.2, this
# repo), libffi, pugixml (for the bundled scanner) - all confirmed present.
#
# SOVERSION 3 (checked upstream CMakeLists.txt at v0.3.1 directly). BUILD_TESTING defaults OFF for
# non-Debug builds (RPM's default %%cmake build type isn't "Debug"), so GTest is not needed.
#
# Real build failure found and fixed: hyprwire's source uses `std::vector::append_range` (a C++23
# library feature) - el10's default GCC 14 (14.4.1) doesn't implement it in libstdc++ yet, even
# with `-std=c++23` (confirmed directly: a trivial test program using append_range fails to
# compile with the default `g++`). Fixed with `gcc-toolset-15` (15.2.1) - an official, opt-in
# newer-GCC package on el10 (not a COPR/third-party toolchain), confirmed the same trivial test
# compiles fine under it. Enabled via the standard `%%enable_gcctoolset15` RPM macro (from
# `/etc/rpm/macros.gcc-toolset-15-enable`, shipped by the `gcc-toolset-15-runtime` package) rather
# than manually exporting CC/CXX. **Real second finding**: `%%enable_gcctoolset15` used as a
# top-level spec macro fails with `Unknown tag` inside a fresh mock chroot - mock's own internal
# `rpmbuild -bs --nodeps` step (which regenerates the SRPM inside the chroot before installing any
# BuildRequires) parses the spec BEFORE `gcc-toolset-15-runtime` (which ships the macro file at
# `/etc/rpm/macros.gcc-toolset-15-enable`) is installed - a real chicken-and-egg problem, not
# something to work around by declaring it differently. Fixed by dropping the top-level macro
# entirely and instead sourcing `/usr/lib/gcc-toolset/15-env.source` directly as a shell command at
# the start of `%%build` - a plain runtime shell action, not something spec-parse-time needs to
# already understand.
# Third finding: RPM's default hardening CFLAGS reference `-specs=.../redhat-annobin-cc1`, which
# needs an annobin plugin matching whichever `cc1` actually runs - gcc-toolset-15's `cc1` can't
# find the SYSTEM gcc's annobin plugin (`cc1: fatal error: inaccessible plugin file
# plugin/annobin.so`). Fixed with `gcc-toolset-15-gcc-plugin-annobin` (the toolset's own matching
# plugin package).
# STATUS: not yet mock-built successfully (append_range, then the macro chicken-and-egg problem,
# then this annobin mismatch).
# ---------------------------------------------------------------------------

Name:           hyprwire
Version:        0.3.1
Release:        1%{?dist}
Summary:        A fast and consistent wire protocol for IPC

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwire
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-toolset-15-gcc-c++
BuildRequires:  gcc-toolset-15-gcc-plugin-annobin
BuildRequires:  cmake
BuildRequires:  pkgconfig(hyprutils) >= 0.9.0
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(pugixml)

%description
Hyprwire is a fast and consistent wire protocol for IPC, used by Hyprland's
hyprctl utility and related tooling.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Header files and pkgconfig data needed to build against hyprwire, and the
`hyprwire-scanner` protocol code generator.

%prep
%autosetup -p1

%build
source /usr/lib/gcc-toolset/15-env.source
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/libhyprwire.so.%{version}
%{_libdir}/libhyprwire.so.3

%files devel
%{_bindir}/hyprwire-scanner
%{_includedir}/hyprwire/
%{_libdir}/libhyprwire.so
%{_libdir}/pkgconfig/hyprwire.pc
%{_libdir}/pkgconfig/hyprwire-scanner.pc
%{_libdir}/cmake/hyprwire-scanner/

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.3.1-1
- Initial dank-ws-copr package, written from scratch (no distro reference spec exists anywhere);
  structured to match this repo's aquamarine/hyprwayland-scanner conventions
