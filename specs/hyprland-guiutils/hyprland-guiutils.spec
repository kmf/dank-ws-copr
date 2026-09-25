# ---------------------------------------------------------------------------
# Written from scratch for dank-ws-copr - no distro spec exists anywhere
# (Fedora rawhide/epel9/epel10 all 404 for both this and its predecessor
# name, hyprland-qtutils). Closes the actual "missing hyprland-guiutils" gap
# this repo was asked to fix - Hyprland itself shells out to these binaries
# for its built-in polkit-agent fallback dialog, file-picker fallback, crash
# reporter, and first-run welcome/update/donate screens. Needed
# specs/hyprtoolkit/ (also written from scratch, see its own header) as a
# hard dependency - built and available in this repo first.
# ---------------------------------------------------------------------------

Name:           hyprland-guiutils
Version:        0.2.2
Release:        1%{?dist}
Summary:        Hyprland GUI utilities (dialog, welcome, update/donate screens)

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-guiutils
Source0:        %{url}/archive/v%{version}/hyprland-guiutils-%{version}.tar.gz

BuildRequires:  gcc-toolset-16-gcc-c++
BuildRequires:  gcc-toolset-16-gcc-plugin-annobin
BuildRequires:  cmake
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0
BuildRequires:  pkgconfig(hyprutils) >= 0.10.2
BuildRequires:  pkgconfig(hyprtoolkit) >= 0.4.0
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libdrm)

Requires:       hyprland

%description
Small GUI utility apps used by Hyprland itself: hyprland-dialog (generic
dialog box, used as a polkit-agent/file-picker fallback), hyprland-run (a
basic run box), and the hyprland-welcome/update-screen/donate-screen
first-run/notification screens. Built on hyprtoolkit, Hyprland's own
native (non-Qt) GUI toolkit.

%prep
%autosetup -n %{name}-%{version}

%build
source /usr/lib/gcc-toolset/16-env.source
%cmake
%cmake_build

%install
source /usr/lib/gcc-toolset/16-env.source
%cmake_install

%files
%license LICENSE
%{_bindir}/hyprland-dialog
%{_bindir}/hyprland-run
%{_bindir}/hyprland-welcome
%{_bindir}/hyprland-update-screen
%{_bindir}/hyprland-donate-screen

%changelog
* Fri Sep 25 2026 Karl Fischer <karl@obsidian.co.za> - 0.2.2-1
- Initial dank-ws-copr package, written from scratch (no distro reference
  spec exists anywhere, under this name or its predecessor
  hyprland-qtutils); closes the reported "missing hyprland-guiutils" gap
