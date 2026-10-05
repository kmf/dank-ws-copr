# ---------------------------------------------------------------------------
# Forked from Terra EL (terrapkg/packages-el, GPL-3.0), fetched directly from
# their published SRPM (https://repos.fyralabs.com/terra44-source/
# mangowm-0:0.17.4-1.fc44.src.rpm) since terrapkg/packages-el's own el10
# branch never carried mangowm past the 0.16.3 reference-only fork
# (specs/mangowm/'s prior git history) - this is Terra's Fedora 44 build,
# adapted for el10.
#
# REAL BUG FOUND in Terra's own spec: it declares `BuildRequires:
# pkgconfig(wlroots-0.19)`, but mango 0.17.4's actual source (meson.build)
# requires `dependency('wlroots-0.20', version: '>=0.20.0')` and
# `dependency('scenefx-0.5', version: '>=0.5.0')` - Terra's spec is stale,
# never updated when upstream mango bumped its wlroots floor (same class of
# staleness as the earlier 0.16.3 assessment in this repo's own PLAN.md).
# Fixed here to declare what the source actually needs: wlroots-0.20 (via
# specs/wlroots0.20/, side-by-side with el10's plain 0.18.2) and scenefx 0.5
# (specs/scenefx/, bumped back from an earlier, now-superseded 0.4.1 pin -
# see that spec's own header).
#
# Also needed pixman bumped to >=0.46.0 (specs/pixman/, SYSTEM-WIDE - safe,
# stable SONAME across this version range, see that spec's header) and
# xkbcommon >=1.8.0 (already satisfied: el10 was bumped to 1.13.1 earlier
# this session for Hyprland, see specs/libxkbcommon/).
#
# Otherwise unmodified from Terra's spec - same structure, meson build,
# %files layout, mangowc Obsoletes/Provides compat chain.
# ---------------------------------------------------------------------------

%global mangowc_ver 0.12.5-1

Name:           mangowm
Version:        0.17.5
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
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(libcjson)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1) >= 0.46.0
BuildRequires:  pkgconfig(scenefx-0.5) >= 0.5.0

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
%{_userunitdir}/mango-session.target

%changelog
* Mon Oct 05 2026 Karl Fischer <karl@obsidian.co.za> - 0.17.5-1
- Update to 0.17.5 (bugfix release; same wlroots-0.20/scenefx-0.5 deps)

* Tue Sep 29 2026 Karl Fischer <karl@obsidian.co.za> - 0.17.4-1
- Forked from Terra's published Fedora 44 SRPM for dank-ws-copr, fixed the
  stale wlroots-0.19/scenefx BuildRequires to match what 0.17.4's actual
  source needs (wlroots-0.20, scenefx-0.5) - see header comment
