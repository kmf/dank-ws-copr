# ---------------------------------------------------------------------------
# Forked/adapted from Fedora's rawhide dist-git for dank-ws-copr:
#   https://src.fedoraproject.org/rpms/wtype/raw/rawhide/f/wtype.spec
# Adapted 2026-10-23, bumped 0.4 -> 0.5 (latest upstream tag). Not in EPEL 10; needed by
# voxtype (Wayland typing backend) in the dank-ws images.
# Release: %%autorelease -> 1%%{?dist}; %%changelog: manual (rpmautospec n/a on el10).
# ---------------------------------------------------------------------------

Name:           wtype
Version:        0.5
Release:        1%{?dist}
Summary:        xdotool type for Wayland
License:        MIT

URL:            https://github.com/atx/wtype
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(xkbcommon)

%description
%{summary}


%prep
%autosetup -n %{name}-%{version}


%build
%meson
%meson_build


%install
%meson_install


%files
%license LICENSE
%doc README.md
%{_bindir}/wtype
%{_mandir}/man1/wtype.1*


%changelog
* Fri Oct 23 2026 Karl Fischer <kmf@fischer.org.za> - 0.5-1
- Import from Fedora rawhide, update to 0.5 for EL10
