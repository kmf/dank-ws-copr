# ---------------------------------------------------------------------------
# Forked from Fedora rawhide, unmodified. el10's own iniparser (from EPEL) is
# the old 4.1 release, which never shipped a pkgconfig file at all (confirmed:
# `rpm -ql iniparser-devel` on el10 has no .pc, just headers + bare .so).
# Needed because hyprtoolkit (specs/hyprtoolkit/) does
# `pkg_check_modules(deps REQUIRED IMPORTED_TARGET ... iniparser ...)` and
# fails outright without one. Fedora's current 4.2.6 switched to CMake and
# does ship libiniparser.pc, so bumping (rather than patching el10's old one)
# was simpler and matches this repo's established pattern for stale
# packages that need a version floor for a Hyprland-ecosystem dependency.
# ---------------------------------------------------------------------------

Name:          iniparser
Version:       4.2.6
Release:       1%{?dist}
Summary:       C library for parsing "INI-style" files

License:       MIT
URL:           https://gitlab.com/%{name}/%{name}
Source0:       https://gitlab.com/%{name}/%{name}/-/archive/v%{version}/%{name}-v%{version}.tar.gz

BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: doxygen

%description
iniParser is an ANSI C library to parse "INI-style" files, often used to
hold application configuration information.

%package devel
Summary:       Header files, libraries and development documentation for %{name}
Requires:      %{name} = %{version}-%{release}

%description devel
This package contains the header files, static libraries and development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%prep
%autosetup -n %{name}-v%{version}

%build
%cmake -DBUILD_TESTS=ON -DBUILD_EXAMPLES=ON
%cmake_build

%install
%cmake_install
rm -rf %{buildroot}%{_bindir}/testrun
rm -rf %{buildroot}%{_bindir}/ressources
rm -rf %{buildroot}%{_docdir}/%{name}/examples

%check
%ctest
%{_vpath_builddir}/iniexample
%{_vpath_builddir}/parse test/ressources/good_ini/twisted.ini

%ldconfig_scriptlets

%files
%doc AUTHORS FAQ*md INSTALL README.md
%license LICENSE
%{_libdir}/libiniparser.so.*

%files devel
%{_libdir}/libiniparser.a
%{_libdir}/libiniparser.so
%{_includedir}/%{name}
%{_libdir}/cmake/%{name}
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Fri Sep 25 2026 Karl Fischer <karl@obsidian.co.za> - 4.2.6-1
- Forked from Fedora rawhide for dank-ws-copr: el10's own iniparser (EPEL,
  4.1) never shipped a pkgconfig file, needed by hyprtoolkit's build
