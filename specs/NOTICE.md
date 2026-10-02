# Third-party spec attribution

Some `.spec` files under `specs/` in this repo are forked/adapted from other projects' packaging
work, per standard Fedora/EPEL packaging-community practice of reusing and adapting spec files
across distros/repos with attribution. Each such file carries a header comment naming its exact
source, license, and what was changed. This file is the index.

| Spec | Forked from | Source license | Status |
|---|---|---|---|
| `specs/ghostty/ghostty.spec` | [Terra EL](https://github.com/terrapkg/packages-el) (`el10` branch) | GPL-3.0 | Adapted; not yet built/tested |
| `specs/mangowm/mangowm.spec` | [Terra EL](https://repos.fyralabs.com/terra44-source/) (Fedora 44 SRPM) | GPL-3.0-or-later AND MIT AND X11 AND CC0-1.0 (see spec's own `License:` tag) | Adapted (fixed a real stale `wlroots-0.19` BuildRequires vs. the source's actual `wlroots-0.20` requirement); verified via real mock build + install |
| `specs/scenefx/scenefx.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/scenefx) | MIT; Fedora packaging convention as above | Adapted (version-bumped); verified via real mock build + install |
| `specs/pixman/pixman.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/pixman) | MIT; Fedora packaging convention as above | Unmodified; verified via real mock build + install |
| `specs/libdrm/libdrm.spec` + patches | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/libdrm) | MIT; Fedora packaging convention as above | Unmodified; verified via real mock build + install |
| `specs/wlroots0.20/wlroots0.20.spec` + patch | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/wlroots) (current unversioned `wlroots`, renamed) | MIT; Fedora packaging convention as above | Adapted (renamed for side-by-side install, same pattern as `specs/wlroots0.19/`); verified via real mock build + install |
| `specs/gtk4-layer-shell/gtk4-layer-shell.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/gtk4-layer-shell) | MIT (package); Fedora spec files are conventionally reusable under the packaged software's own license or CC0 per Fedora packaging norms | Adapted; verified via real mock build + install |
| `specs/greetd/greetd.spec` + auxiliary files (`.fc`, `.pam`, `.sysusers`, `.tmpfiles`, patches) | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/greetd) | GPL-3.0-only AND Apache-2.0 AND more (see spec's own `License:` tag); Fedora packaging convention as above | Adapted; verified via real mock build + install |
| `specs/rust-pam-sys/rust-pam-sys.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/rust-pam-sys) | rust2rpm-generated; Fedora packaging convention as above | Adapted; verified via real mock build |
| `specs/rust-enquote/rust-enquote.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/rust-enquote) | rust2rpm-generated; Fedora packaging convention as above | Adapted; verified via real mock build |
| `specs/rust-greetd_ipc/rust-greetd_ipc.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/rust-greetd_ipc) | rust2rpm-generated; Fedora packaging convention as above | Adapted; verified via real mock build |
| `specs/rust-rpassword5/rust-rpassword5.spec` + patch | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/rust-rpassword5) | rust2rpm-generated; Fedora packaging convention as above | Adapted; verified via real mock build |
| `specs/iniparser/iniparser.spec` | [Fedora rawhide dist-git](https://src.fedoraproject.org/rpms/iniparser) | MIT; Fedora packaging convention as above | Unmodified; verified via real mock build + install |
| `specs/kitty/kitty.spec` | [Fedora dist-git](https://src.fedoraproject.org/rpms/kitty) (`epel10` branch) | GPL-3.0-only AND more (see spec's own `License:` tag); Fedora packaging convention as above | Adapted (version-bumped 0.47.1→0.49.2, regenerated go-vendor-tools archive, vendored a prebuilt `slangc` as a new build-time tool); verified via real mock build + install |

Terra EL's `packages-el` repo is licensed GPL-3.0 as a whole. Per GPLv3, redistributed/modified
files from it retain that license and must credit the source — done via the header comment in each
adapted file plus this index. This does not relicense the rest of `dank-ws-copr`; only the files
explicitly marked above carry GPL-3.0 provenance.
