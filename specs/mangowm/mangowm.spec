# ---------------------------------------------------------------------------
# Forked from Terra EL (terrapkg/packages-el, branch `el10`, GPL-3.0) verbatim, for reference:
#   https://github.com/terrapkg/packages-el/blob/el10/anda/desktops/mangowm/mangowm.spec
# Fetched into dank-ws-copr on 2026-09-24. NOT ADAPTED, NOT BUILDABLE YET.
#
# BLOCKED: requires pkgconfig(wlroots-0.19); el10's EPEL only ships wlroots 0.18.2, and Terra EL
# itself does not appear to package wlroots at all (checked: no `wlroots` entry under
# terrapkg/packages-el's anda/lib/), meaning this spec is likely unbuildable in Terra EL too, not
# just here. Also needs `scenefx-devel`, which Terra EL *does* package (anda/lib/scenefx) and
# which we have not yet ported. See SETUP.md Step 9 for full detail.
#
# Recommendation: deprioritize below ghostty (which only needs one missing dependency,
# gtk4-layer-shell, vs. mangowm's two - one of which, a newer wlroots, is a much bigger lift and
# carries real risk of colliding with the wlroots 0.18.2 that niri and other consumers depend on).
# ---------------------------------------------------------------------------

%global mangowc_ver 0.12.5-1

Name:           mangowm
Version:        0.16.3
Release:        1%{?dist}
Summary:        A modern, lightweight, high-performance Wayland compositor built on dwl
License:        GPL-3.0-or-later AND MIT AND X11 AND CC0-1.0
Packager:       Olivia <git@olivia.sh>
URL:            https://github.com/mangowm/mango
Source:         %{url}/archive/%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wlroots-0.19)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(libcjson)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  scenefx-devel

Conflicts:      mangowc < %{mangowc_ver}
Obsoletes:      mangowc < %{mangowc_ver}
Provides:       mangowc = %{mangowc_ver}

%description
MangoWM is a modern, lightweight, high-performance Wayland compositor built on
dwl — crafted for speed, flexibility, and a customizable desktop experience.

%prep
%autosetup -n mango-%{version}

%build
%meson
%meson_build

%install
%meson_install

%files
%doc README.md
%license LICENSE
%{_bindir}/mango
%{_bindir}/mmsg
%{_sysconfdir}/mango/config.conf
%{_datadir}/wayland-sessions/mango.desktop
%{_datadir}/xdg-desktop-portal/mango-portals.conf
%{_mandir}/man1/mmsg.1.*

%changelog
* Sun Jul 19 2026 Olivia <git@olivia.sh> - 0.15.4-2
- Update packager

* Wed Mar 04 2026 Olivia <git@olivia.sh> - 0.12.5-1
- Rename to mangowm

* Wed Nov 12 2025 Olivia <git@olivia.sh>
- Package mangowc
