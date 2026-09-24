# Dank Material Shell — CentOS Stream 10 Packaging

## Goal
Build and host DMS shell + dependency RPMs for **CentOS Stream 10**, hosted on GitHub, built via COPR.

- Repo: `gh kmf/dank-ws-copr`
- Build host: `durin` (Tailscale-connected, CentOS Stream 10)
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

## Known Blockers (tracked separately — different root causes)

_Updated 2026-09-24 after hands-on verification on `durin` — see `SETUP.md` Steps 5–7 for full
commands/output. Several original entries were stale._

| Package | Issue | Likely fix path |
|---|---|---|
| niri | ~~COPR doesn't install on el10~~ **RESOLVED — false alarm.** `dnf install niri` resolves and installs cleanly today (only extra dep is `libseat` from EPEL). Confirmed via dry-run + smoke test. | None — ship it |
| greetd | Not confirmed in EPEL10. **Confirmed: not a toolchain issue** — Rust is an official AppStream package (1.98.1) on el10. This is purely an unwritten/unbranched spec. `dms-greeter`/`dms-greeter-git` are hard-blocked on this (verified: `nothing provides greetd`). | Write a from-scratch EL10 spec (small, all-Rust project — low risk) |
| ghostty | Needs Zig toolchain. **Confirmed available**: `zig-0.15.2` ships from official EPEL10, no COPR/custom repo needed. **Spec forked/adapted** from Terra EL into `specs/ghostty/ghostty.spec` (see SETUP.md Step 9) — down to a single real blocker: `gtk4-layer-shell` doesn't exist on el10 anywhere (incl. Terra). That spec has also been forked (from Fedora rawhide) into `specs/gtk4-layer-shell/` and looks like a clean, low-risk port. Neither has been mock-built/verified yet. | Install `mock`, build `gtk4-layer-shell` first, then `ghostty` |
| hyprland | COPR (lionheartp/Hyprland) has no el10/CentOS-Stream-10 target. Base `wlroots-0.18.2`/`wlroots-devel` are fine (EPEL); the gap is Hyprland's own newer libs (`aquamarine`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics`). **Worse than previously framed**: Terra EL (see Related Links) — a third party actively packaging for el10 — deliberately *removed* Hyprland from their repo, stating plainly "they don't build anymore and we don't support hyprland as a WM, esp since the whole freedesktop thing." This isn't just "no COPR target," it's an informed third party judging Hyprland currently unbuildable/unsupportable on this kind of platform. Terra does still carry specs for most of the dependency libs (`hyprutils`, `hyprlang`, `hyprgraphics`, `hyprwayland-scanner`, `hypridle`, `hyprlock`) but not Hyprland core itself, nor `aquamarine`/`hyprcursor`. | **Recommend deprioritizing** below mangowm/niri rather than treating as a straightforward 5-lib port |
| miraclewm | Not wlroots-based (Mir). Confirmed absent from all enabled repos; not investigated further yet. | Separate investigation track — different dependency stack (Mir, mir-graphics-drivers), may not exist on EL10 |

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

**CentOS Stream 10 / EPEL setup**
- https://doc.fedoraproject.org/cs/epel/getting-started
- https://github.com/AvengeMedia/DankMaterialShell/blob/master/core/internal/distros/fedora.go
