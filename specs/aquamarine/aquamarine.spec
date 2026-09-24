# ---------------------------------------------------------------------------
# Written from scratch for dank-ws-copr - no Fedora, Terra, or any other distro spec exists for
# aquamarine anywhere (checked: Fedora rawhide/epel9/epel10 all 404; Terra never packaged it,
# checked their anda/lib directory listing directly - see SETUP.md Step 8/15). Needed because
# `hyprland` requires `aquamarine>=0.9.3` (Hyprland's own rendering/backend library, replacing
# direct wlroots usage since Hyprland ~0.40+).
#
# Structured to match the same CMake-project conventions used for hyprutils/hyprcursor/
# hyprgraphics in this repo (all from the same hyprwm org, same build-system idioms), since
# aquamarine's own upstream CMakeLists.txt follows an identical pattern to those. Full dependency
# sweep against el10 before writing this: hyprwayland-scanner>=0.4.0 (have 0.4.2, this repo),
# libseat>=0.8.0, libinput>=1.26.0, wayland-client/wayland-protocols, hyprutils>=0.8.0 (have 0.14.2,
# this repo, bumped from Fedora's stale 0.7.1), pixman-1, libdrm, gbm, libudev, libdisplay-info,
# hwdata, OpenGL/GLES3 (mesa-libGLES-devel, confirmed present via a real hyprgraphics build) - all
# confirmed present/satisfiable.
#
# SOVERSION 14 (checked upstream CMakeLists.txt at v0.15.1 directly:
# `set_target_properties(aquamarine PROPERTIES VERSION ... SOVERSION 14)`).
# STATUS: not yet mock-built - first genuinely from-scratch spec this session with a full upstream
# CMakeLists.txt as the only reference (no other distro's packaging to structurally crib from).
# ---------------------------------------------------------------------------

Name:           aquamarine
Version:        0.15.1
Release:        1%{?dist}
Summary:        A very light linux rendering backend library

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/aquamarine
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  mesa-libGLES-devel
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(libseat) >= 0.8.0
BuildRequires:  pkgconfig(libinput) >= 1.26.0
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(hyprutils) >= 0.8.0
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(hwdata)

%description
Aquamarine is a very light linux rendering backend library. It abstracts
away all the necessary parts about writing a Wayland compositor, like DRM
modesetting, EGL/OpenGL rendering, and Wayland backend windowing, along with
libinput and libseat for input and session management, allowing you to
focus on the actual compositor part.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Header files and pkgconfig data needed to build Wayland compositors
against aquamarine, most notably Hyprland.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libaquamarine.so.%{version}
%{_libdir}/libaquamarine.so.14

%files devel
%{_includedir}/aquamarine/
%{_libdir}/libaquamarine.so
%{_libdir}/pkgconfig/aquamarine.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 0.15.1-1
- Initial dank-ws-copr package, written from scratch (no distro reference spec exists anywhere);
  structured to match this repo's hyprutils/hyprcursor/hyprgraphics conventions
