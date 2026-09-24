# ---------------------------------------------------------------------------
# Written from scratch for dank-ws-copr - no Fedora or Terra spec exists for muparser anywhere
# (checked: 404 on Fedora rawhide/epel9/epel10). Needed because `hyprland` requires
# `pkgconfig(muparser)`. Used openSUSE's official `science/muparser` spec
# (https://build.opensuse.org/package/show/science/muparser) as a structural reference for the
# %%files layout, but rewritten in Fedora/el packaging style rather than openSUSE conventions
# (dropped their soname-versioned `libmuparser2_3_5` package-name scheme and an unavailable
# `muparser-abiversion.diff` patch - not needed for our purposes: hyprland just wants a plain
# `pkgconfig(muparser)`, no specific soname-in-package-name convention).
#
# All build deps (cmake, gcc-c++, OpenMP via gcc) confirmed present on el10 - muparser's own
# CMakeLists.txt has no exotic requirements.
# STATUS: not yet mock-built.
# ---------------------------------------------------------------------------

Name:           muparser
Version:        2.3.5
Release:        1%{?dist}
Summary:        A fast math parser library for C++

License:        MIT
URL:            https://beltoforion.de/en/muparser/
Source0:        https://github.com/beltoforion/muparser/archive/v%{version}/muparser-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++

%description
muParser is an extensible math expression parser library written in C++. It
works by transforming a mathematical expression into bytecode and
precalculating constant parts of the expression.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Header files, CMake config, and pkgconfig data needed to build applications
that use muparser.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc CHANGELOG
%{_libdir}/libmuparser.so.2*

%files devel
%{_includedir}/muParser*.h
%{_libdir}/libmuparser.so
%{_libdir}/cmake/muparser/
%{_libdir}/pkgconfig/muparser.pc

%changelog
* Thu Sep 24 2026 Karl Fischer <karl@obsidian.co.za> - 2.3.5-1
- Initial dank-ws-copr package, written from scratch (no upstream distro reference spec found);
  structurally informed by openSUSE's science/muparser spec but rewritten Fedora/el-style
