# Dank Material Shell — CentOS Stream 10 Packaging

## Goal — the actual deliverable, stated plainly
The end goal is **not** "have working spec files somewhere" — it's a real, live **COPR repo
(`kmf/dank-ws-copr`)** that any CentOS Stream 10 machine can add and install DMS + its dependency
chain from, the same way one would `dnf copr enable avengemedia/danklinux` today. Concretely, done
looks like:

```
dnf copr enable kmf/dank-ws-copr
dnf install dms dms-greeter quickshell   # (and whatever else has been ported)
```
actually working on a fresh CentOS Stream 10 box — not just "the SRPM built in a local mock chroot
on durin". Everything else in this doc (the dependency tree, the blockers table, the fork-vs-adopt
decision on Terra) is in service of that one artifact.

**Where things stand**: as of 2026-09-24, `specs/` in this repo (`kmf/dank-ws-copr`, currently local
to `durin` only — see below) holds 6 forked/adapted spec packages, each individually verified via a
real `mock` build + `dnf install` + smoke test (not just written and hoped): `gtk4-layer-shell`,
`rust-pam-sys`, `rust-enquote`, `rust-greetd_ipc`, `rust-rpassword5`, `greetd`. **None of this is
live yet** — there is no GitHub repo pushed, no COPR project created, and no CI wiring. The
verification so far proves the specs *work*, not that the end-to-end distribution goal is met.
Turning this into the actual artifact needs, roughly in order:
1. ✅ **Done 2026-09-24**: pushed to a real `kmf/dank-ws-copr` GitHub repo — public, live at
   https://github.com/kmf/dank-ws-copr. (SSH auth to GitHub as `kmf` needed `github.com`'s host key
   added to `known_hosts` first — one-time setup, see SETUP.md Step 12.)
2. Create the actual `kmf/dank-ws-copr` COPR project (copr.fedorainfracloud.org), pointed at that
   GitHub repo, targeting CentOS Stream 10 (+ EPEL as a dependency source, per below). `copr-cli`
   is now installed on `durin`, but **needs an API token tied to your Fedora Account** (generate at
   copr.fedorainfracloud.org/api/ once logged in, then `copr-cli` picks it up from
   `~/.config/copr`) — this is a manual step only you can do, not something automatable from here.
3. Decide and wire up the CI trigger model (Open Question 1) so pushes actually build.
4. Get the already-verified specs building successfully *in COPR's own build environment*, not just
   locally on `durin`'s mock — COPR's chroot/mock config should match, but this hasn't been
   confirmed with a real COPR build yet.
5. ✅ **Done 2026-09-27**: validated the actual `dnf copr enable kmf/dank-ws-copr && dnf install ...`
   flow — found and fixed a real chroot-detection bug in the process (see "Repos to Enable on
   `durin`" below). Still only validated on `durin` itself, not yet on a separate machine.

- Repo: `gh kmf/dank-ws-copr` (**local git repo only so far — not yet pushed to GitHub**)
- Build host: `durin` (Tailscale-connected, CentOS Stream 10) — used for spec development and
  local `mock` verification; the actual COPR builds happen on Copr's own infrastructure once step 2
  above is done, not on `durin` itself
- Commit convention: Conventional Commits
- EPEL is enabled on the build host as a dependency source (CRB + epel-release), not a separate packaging target — we're not double-tracking EPEL10 and CentOS-Stream-10 as parallel goals.

## Build Environment Setup (do first)

**Status: DONE on `durin` (2026-09-24).** EPEL was already installed/enabled; only CRB needed
enabling. Full reproducible step log: `SETUP.md`.
```
dnf config-manager --set-enabled crb
dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm   # was already present
```
Then repoquery the full dependency list below against the enabled repos to see what's already available upstream vs. what actually needs a port. No point porting a spec that just needs an EPEL10 branch request.

**Repoquery sweep result:** Tiers 1–3 are already fully built and available — see `SETUP.md` Step 5
for the full package/version/source-repo table. Tier 4 gap analysis is in the Known Blockers table
below.

## Dependency Tree (build order)

**Tier 1 — core libs — ✅ all available on el10 today** (via `avengemedia/danklinux` COPR)
breakpad, cli11, cpptrace, matugen

**Tier 2 — shell components (depend on Tier 1) — ✅ all available on el10 today** (same COPR)
quickshell / quickshell-git, dgop, danksearch, cliphist, dankcalendar-git

**Tier 3 — shell packages (depend on Tier 2) — ✅ available, with one naming caveat**
dms, dms-greeter, dms-greeter-git all install and smoke-test clean (see `SETUP.md` Step 6).
`dms-git` is **not a separate package name** — the binary RPM is always called `dms`; git-snapshot
builds are just higher epoch/version of the same `dms` package, sourced from the
`avengemedia/dms-git` COPR. No separate stable `avengemedia/dms` repo was found enabled or
populated on this host — see Open Question #2 below, now more concrete.

**Tier 4 — runtime alternatives (not build-time deps of DMS itself)**
- Compositors: niri, hyprland, mangowm, miraclewm
- Terminals: kitty, alacritty, ghostty
- Fonts/theming: material-symbols-fonts, qt6ct-kde
- Greeter: greetd

Treat Tier 4 as install-time choices, not a monolithic build requirement — DMS ships once Tiers 1–3 are green.

**Tier 5 — optional features surfaced by `dms doctor`**
- `kimageformats` — ✅ **no fork needed.** `dms doctor` checks for the plain `kimageformats` name,
  but the real package on el10 is `kf6-kimageformats` (KF6, not the unrelated `qt6-imageformats`
  which is separate and already installed) — already ships directly in **EPEL** (`6.30.0-1.el10_4`),
  confirmed via `dnf install kf6-kimageformats`. Just an install-time step, not a packaging gap.
- `cava` — ✅ forked into `kmf/dank-ws-copr` (`specs/cava/`), real COPR build succeeded (11031735).
  Unmodified from Fedora rawhide's spec (no epel9/epel10 branch existed there); all its
  BuildRequires (alsa-lib-devel, fftw-devel, pulseaudio-libs-devel, ncurses-devel, iniparser-devel)
  are already on el10 BaseOS/AppStream/CRB, so no dependency chain to chase.
- `hyprland-guiutils` — ✅ **forked, along with a new dependency chain (2 more packages), all
  written from scratch — genuinely unpackaged anywhere, not even Fedora.** Hyprland itself shells
  out to these binaries for its built-in polkit-agent fallback, file-picker fallback, crash
  reporter, and first-run welcome/update/donate screens. Chain, in build order:
  - `iniparser` bumped 4.1→4.2.6 (forked from Fedora rawhide) — el10's own (from EPEL/BaseOS) never
    shipped a pkgconfig file at all, needed by `hyprtoolkit`'s CMake. **Real, narrow conflict**:
    bumping changes `libiniparser`'s SONAME (`.so.1`→`.so.4`), breaking `daxctl`/`ndctl`/`netatalk`
    if installed (all real CentOS/EPEL packages) — accepted as low-risk for a desktop-shell-focused
    repo (same class of decision as the lua/wireplumber conflict below), unlike that one this
    doesn't affect any package a typical desktop-shell user would have installed. `cava` (built
    earlier, links `libiniparser.so.1`) was rebuilt against the new version to match.
  - `hyprtoolkit` — written from scratch (Hyprland's own *native, non-Qt* GUI toolkit, its
    predecessor `hyprland-qtutils` was Qt-based but got replaced entirely). Built directly on
    aquamarine/hyprutils/hyprlang/hyprgraphics, all already in this repo. Hit two real bugs: (1) a
    genuine, still-unfixed-upstream-on-`main` bug — `PANGO_WRAP_NONE` has never existed in any
    Pango release (checked el10's actual 1.54.0 headers directly) — patched to `PANGO_WRAP_WORD_CHAR`;
    (2) the same GCC14/libstdc++ completeness-gap pattern hit repeatedly this session, this time
    `std::format` lacking a range formatter for `std::vector<std::string>` — fixed with
    `gcc-toolset-16` (same one Hyprland itself needed).
  - `hyprland-guiutils` itself — written from scratch, builds clean once the above two are in place.
  Real COPR builds queued 2026-09-25 (iniparser 11035226 → cava rebuild 11035228, hyprtoolkit
  11035229 → hyprland-guiutils 11035230, in dependency order).

## Known Blockers (tracked separately — different root causes)

_Updated 2026-09-24 after hands-on verification on `durin` — see `SETUP.md` Steps 5–7 for full
commands/output. Several original entries were stale._

| Package | Issue | Likely fix path |
|---|---|---|
| niri | ~~COPR doesn't install on el10~~ **RESOLVED — false alarm.** `dnf install niri` resolves and installs cleanly today (only extra dep is `libseat` from EPEL). Confirmed via dry-run + smoke test. | None — ship it |
| greetd | ✅ **RESOLVED — built, installed, and verified working.** Forked from Fedora rawhide (unbranched for EPEL, not broken/unported). Needed 4 supporting crate packages forked the same way, all also just unbranched Fedora packages: `rust-pam-sys`, `rust-enquote`, `rust-greetd_ipc` (path-dep quirk in cargo2rpm's BR generation), `rust-rpassword5` (greetd's Cargo.lock pins an old major version). Real mock build succeeded, real `dnf install` succeeded, `rpm -V`/`ldd`/`greetd --help` all clean. **Confirmed the original hard blocker is gone**: `sudo dnf install --assumeno dms-greeter` now resolves cleanly end-to-end. See SETUP.md Step 11 for the full trail. | Done — upload these 6 specs to the actual COPR (see restated Goal below) |
| ghostty | ✅ **RESOLVED — built, installed, and verified working.** `gtk4-layer-shell` (forked from Fedora rawhide) unblocked the dependency gap; the deeper Zig `--system`-mode issue (six C dependencies including `harfbuzz` all silently flip their "prefer system vs. vendored" default under offline mode, not just the one the error message named) was isolated via a real network-enabled host build vs. an isolated `--system`-mode repro, then fixed by passing `-fno-sys=` for the full set of six. Also found and fixed a second, unrelated real bug along the way: `%{evr}` isn't a defined macro on el10 at all — it was silently baking the literal string into built RPMs' dependency metadata, making every ghostty subpackage genuinely uninstallable. Real mock build succeeded (17 RPMs), real `dnf install` succeeded, `rpm -V`/`ldd`/`ghostty --version` all clean. See SETUP.md Step 13 for the full diagnostic trail. | Done — upload to the actual COPR (see restated Goal) |
| mangowm | ✅ **RESOLVED 2026-09-29 — builds successfully, real COPR builds succeeded on both chroots.** User supplied a link to Terra's current Fedora 44 SRPM for mangowm 0.17.4; fetching and inspecting it directly found the same staleness pattern as the earlier 0.16.3 assessment: Terra's own `mangowm.spec` still declares `BuildRequires: pkgconfig(wlroots-0.19)`, but 0.17.4's actual source (`meson.build`) requires `wlroots-0.20 >=0.20.0` and `scenefx-0.5 >=0.5.0` — confirmed by extracting the SRPM and reading meson.build directly, not assumed. `xkbcommon` >=1.8.0 was already satisfied (bumped to 1.13.1 earlier this session for Hyprland). Full chain built, in order: `pixman` bumped 0.43.4→0.46.4 (Fedora rawhide fork, **system-wide** — confirmed same `libpixman-1.so.0` SONAME across this version range via a real reverse-dependency check, so existing consumers keep working unrebuilt, unlike the real SONAME-breaking lua/iniparser conflicts); `libdrm` bumped 2.4.128→2.4.134 (Fedora rawhide fork, also system-wide, same SONAME-stability reasoning — found genuinely necessary via a real failed build: wlroots' own meson.build hard-enforces `>=2.4.129`, not just an RPM spec pin); `wlroots0.20` (Fedora's current unversioned `wlroots` spec, renamed to install side-by-side with el10's plain `wlroots` 0.18.2 which `cage` still depends on — same pattern as the existing `wlroots0.19` package); `scenefx` bumped back to 0.5/wlroots-0.20 (superseding the earlier 0.4.1/wlroots-0.19 pin, since that decision's premise — mango needing wlroots-0.19 — turned out to be based on Terra's stale spec, not mango's real requirement); `mangowm` itself, corrected to declare what 0.17.4 actually needs. Real mock build + local install + smoke test (`mango --help`, `ldd`, `rpm -V` all clean) succeeded first try once the chain was in place; regression-checked `Hyprland`/`niri` still work after the system-wide pixman/libdrm bump. Real COPR builds (both `centos-stream-10-x86_64` and `epel-10-x86_64`): `pixman` 11047470/11047484, `libdrm` 11047472/11047487, `wlroots0.20` 11047474/11047491, `scenefx` 11047475/11047492, `mangowm` 11047476/11047494 — all 10 succeeded. | Done — live on both COPR chroots |
| hyprland | ✅ **RESOLVED — builds successfully, real COPR build 11031343 succeeded.** Full chain: `aquamarine`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics`, `hyprwayland-scanner`, `hyprwire`, `hyprland-protocols` (all from-scratch or forked-and-fixed), plus `libxkbcommon`/`lua`/`muparser` bumped/forked to satisfy version floors. Needed `gcc-toolset-16` (el10's default GCC 14 has real libstdc++ gaps against the C++23/26 features this codebase uses — `std::vector::append_range`, `std::ranges::starts_with` — both confirmed missing via real compile failures, both official opt-in el10 packages, not COPR/third-party). Vendored `glaze` (header-only JSON lib, FetchContent-overridden to a local copy) and the exact `udis86` submodule commit Hyprland pins. **Known open issue**: `lua` 5.5.1 (needed for `lua>=5.5,<5.6`) collides with el10's own `lua-libs` 5.4, which `wireplumber`/`ibus-libpinyin` depend on — confirmed via a real local install attempt, not forced through. Real packaging-strategy decision needed before this ships broadly (side-by-side lua rename vs. accept the conflict vs. something else) — not a build blocker. Terra's dropped Hyprland core turned out to matter less than feared — Fedora rawhide had references for most of the real gaps (unbranched to EPEL, same pattern throughout this repo). `aquamarine`, `hyprwire`, and `hyprland` itself were the only genuinely from-scratch specs (no reference anywhere). See SETUP.md Steps 15–18 for the full trail. **Real, separate runtime gap found 2026-09-25 via live testing**: `dms` (the DMS shell) never actually started on login under Hyprland. Root cause confirmed by reading Hyprland's own source directly: unlike niri (whose `niri-session` wrapper natively activates `graphical-session.target`), plain Hyprland has *zero* built-in systemd session integration — `dms.service`'s `WantedBy=graphical-session.target` never fires under it. Fix (matching DMS's own documented Hyprland guidance): run `dms setup headless --compositor hyprland --no-systemd`, which deploys a direct `hl.on("hyprland.start", ...) -> dms run` exec hook into `hyprland.lua` instead of relying on the systemd target at all. `dank-install-el10.sh` was missing this step entirely (only installed packages + `systemctl --user enable --now dms`, never `dms setup`) — now fixed there for niri/hyprland (mango too, once buildable); `dms setup` doesn't support `miracle-wm` at all (confirmed: `unknown compositor "miracle-wm"`), left as a documented gap. | Done — upload to the actual COPR (already done: build 11031343) |
| miraclewm | ⚠️ **Correction (2026-09-24): this row was wrong.** Initial research checked the wrong package names (`miraclewm`, `mir-libs`, `miral`, `mircommon` as separate dist-git repos) and concluded the whole Mir toolkit was unpackaged anywhere — user correctly pushed back. The real names are `mir` (a single spec building `miral`/`mircommon`/`mirserver`/`mirwayland`/etc. as subpackages) and `miracle-wm` (hyphenated), **both real, actively-maintained Fedora packages** (`mir` updated Sep 21 2026, `miracle-wm` Sep 21 2026) — there's even an official Fedora Spin for it. Full dependency sweep against el10 found nearly everything already present, including niche ones (`wlcs`, `glm-devel`, `gflags-devel`); 2 more deps genuinely missing (`umockdev`, `python-dbusmock` — both forked from Fedora rawhide; turned out to be needed unconditionally at CMake *configure* time, not just test-execution as first assumed, confirmed via two real failed builds). `mir`'s C++ source also hit real GCC 14 libstdc++ completeness gaps (`std::optional::value_or({...})` brace-init overload resolution) — fixed with `gcc-toolset-15` (official opt-in newer-GCC package on el10). ✅ **RESOLVED — both `mir` (real COPR build 11031169) and `miracle-wm` (11031307) succeeded.** See SETUP.md Steps 15–18. | Done |

**Bottom line:** none of the remaining Tier 4 gaps are blocked on missing build infrastructure —
`rust`, `cargo`, `zig`, and `mock` are all official, already-available el10 packages, and disk space
on `durin` is not a constraint (59G free). Every remaining gap is spec-writing work of varying size,
not an infrastructure blocker.

## Repos to Enable on `durin`
- CRB (`dnf config-manager --set-enabled crb`) — ✅ enabled
- epel-release-latest-10 — ✅ already present
- COPR: avengemedia/danklinux — ✅ already enabled (covers Tiers 1–2 + dms-greeter/-git)
- COPR: avengemedia/dms-git — ✅ already enabled (covers `dms`, incl. git-snapshot builds)
- COPR: avengemedia/dms (stable) — ⚠️ **not found enabled, and no evidence it's populated for
  el10** — only `dms-git` provides the `dms` package on this host today. Needs confirming with
  upstream whether this repo exists/has el10 builds at all.
- COPR: yalter/niri — ✅ already enabled, niri installs cleanly (see Known Blockers)
- (pending) COPR target for Hyprland once its own dependency chain (aquamarine, hyprutils,
  hyprlang, hyprcursor, hyprgraphics) is packaged for el10 — see Known Blockers

**Real bug found and fixed 2026-09-27**: `sudo dnf copr enable kmf/dank-ws-copr` failed outright on
a freshly-tested el10 host with `Repository 'epel-10-x86_64' does not exist in project
'kmf/dank-ws-copr'. Available repositories: 'centos-stream-10-x86_64'`. Root cause: a newer
`dnf-plugins-core` auto-detects the local Copr chroot name as `epel-10-x86_64` (Copr's generic
"Enterprise Linux 10" chroot, covering RHEL/CentOS Stream/Rocky/Alma uniformly), not the
CentOS-Stream-specific `centos-stream-10-x86_64` this project had only ever built for. Fixed by
adding the `epel-10-x86_64` chroot (`copr-cli modify kmf/dank-ws-copr --chroot
centos-stream-10-x86_64 --chroot epel-10-x86_64`) and rebuilding all 33 packages for it in
dependency order — Copr chroots don't share build artifacts with each other, so the new chroot
started completely empty. All 33 succeeded (72/72 real builds total across both chroots now).
Verified live: `dnf copr enable` succeeds, `hyprland`/`dms`/`cava` all resolve and dry-run install
cleanly. Full detail in `TESTING.md`'s "Runtime bugs found and fixed" section.

## Open Questions
1. CI trigger model — Packit/webhook on push to `dank-ws-copr`, or manual `copr-cli build` from `durin`? Decides how granular commit scoping needs to be.
2. Do we ship both `dms` and `dms-git` for CentOS Stream 10, or stable-only first pass? **Narrowed
   by findings above:** since only `avengemedia/dms-git` appears to actually exist/be populated for
   el10 today (no stable `avengemedia/dms` el10 builds found), this may not be our choice to make
   yet — need to confirm with upstream whether a stable channel exists before deciding.
3. Validation step — smoke-test on an actual CentOS Stream 10 desktop, or install-success only?
   **Partial answer:** did an install-success + `rpm -V` + `ldd` + binary-runs smoke test on
   `durin` (headless build host) for `dms`/`dms-cli`/`quickshell-git`/`matugen` — all clean (see
   `SETUP.md` Step 6). This doesn't cover actual GUI/Wayland-session rendering, so a real desktop
   smoke test is still open if that level of validation is wanted.

## Side project — `scripts/dank-install-el10.sh`

AvengeMedia's own `dankinstall` (`curl -fsSL https://install.danklinux.com | sh`) doesn't support
RHEL/CentOS/EPEL at all (Arch, Fedora, Ubuntu 26.04+, Debian 13+, openSUSE Tumbleweed, Gentoo only).
`scripts/dank-install-el10.sh` is a flag-driven (non-interactive, v1) shell-script equivalent for
el10: enables EPEL + CRB + `avengemedia/danklinux` + `avengemedia/dms-git` + `kmf/dank-ws-copr`
(+ `yalter/niri` if niri is chosen), installs the Tier 1/2 deps, the chosen compositor
(`niri`/`hyprland`/`miracle-wm`) and terminal (`ghostty`/`kitty`/`alacritty`), `dms` + `dms-greeter`,
and enables the `dms` systemd user service. Refuses `--compositor hyprland` if
`wireplumber-libs`/`ibus-libpinyin` are already installed (the known lua conflict, see `Known
Blockers` above) unless `--force` is passed. Not yet run against a real fresh el10 box end-to-end -
only dry-run tested so far.

## Related Links

**Core Dank COPR**
- https://copr.fedorainfracloud.org/coprs/avengemedia/danklinux/
- https://copr.fedorainfracloud.org/coprs/avengemedia/dms-git/
- https://copr.fedorainfracloud.org/coprs/avengemedia/dms

**Dank Wayland Compositor Links**
- https://copr.fedorainfracloud.org/coprs/lionheartp/Hyprland/
- https://copr.fedorainfracloud.org/coprs/yalter/niri/
- https://copr.fedorainfracloud.org/coprs/lumarel/ghostty/

**Reference specs**
- https://gitlab.com/lumarel/ghostty-rpm/-/blob/master/ghostty.spec?ref_type=heads
- **Terra EL** (`terrapkg/packages-el`, default branch `el10` — third-party repo explicitly targeting
  EL10/CentOS Stream 10, requires EPEL): https://github.com/terrapkg/packages-el — has full specs for
  `dank-material-shell` (Obsoletes/Provides `dms`/`dms-cli`!), `breakpad`, `ghostty` (3 channels),
  `mangowm` (needs newer wlroots-0.19 than el10's current EPEL 0.18.2), and most of Hyprland's dep
  libs — but Hyprland core was deliberately removed by them. Still not enabled as a live repo on
  `durin` (their bootstrap uses `--nogpgcheck`, never approved) — **decision made: fork/adapt their
  spec files into our own repo instead of depending on their infra.** `ghostty` and `mangowm` specs
  have been forked into `specs/` (see SETUP.md Step 9); Tier 1-3 deliberately stayed on the
  already-working `avengemedia` COPRs rather than also forking their `dank-material-shell`/`breakpad`
  specs, since those already work today.

**Standing decision (2026-09-24, explicit): always prefer `avengemedia` over Terra (or any other
third-party source) when both provide the same package.** Settles the DMS build-vs-adopt question
from earlier for good: keep consuming `avengemedia`'s `dms`/`dms-cli` rather than switching to
Terra's `DankMaterialShell` spec, even though Terra's is arguably "more properly" packaged
(Obsoletes/Provides chain, systemd user unit, etc.) — not worth it since avengemedia's already
works and is the upstream-affiliated channel. Applies going forward to any future package choice
where both exist, not just this one.

**CentOS Stream 10 / EPEL setup**
- https://doc.fedoraproject.org/cs/epel/getting-started
- https://github.com/AvengeMedia/DankMaterialShell/blob/master/core/internal/distros/fedora.go
