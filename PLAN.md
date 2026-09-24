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
1. Push this local git history to a real `kmf/dank-ws-copr` GitHub repo (currently just a local
   `git init`, no remote configured — see PLAN.md "Repos to Enable" and SETUP.md for host setup).
2. Create the actual `kmf/dank-ws-copr` COPR project (copr.fedorainfracloud.org), pointed at that
   GitHub repo, targeting CentOS Stream 10 (+ EPEL as a dependency source, per below).
3. Decide and wire up the CI trigger model (Open Question 1) so pushes actually build.
4. Get the already-verified specs building successfully *in COPR's own build environment*, not just
   locally on `durin`'s mock — COPR's chroot/mock config should match, but this hasn't been
   confirmed with a real COPR build yet.
5. Validate the actual `dnf copr enable kmf/dank-ws-copr && dnf install ...` flow works, ideally on
   a machine other than `durin`.

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

## Known Blockers (tracked separately — different root causes)

_Updated 2026-09-24 after hands-on verification on `durin` — see `SETUP.md` Steps 5–7 for full
commands/output. Several original entries were stale._

| Package | Issue | Likely fix path |
|---|---|---|
| niri | ~~COPR doesn't install on el10~~ **RESOLVED — false alarm.** `dnf install niri` resolves and installs cleanly today (only extra dep is `libseat` from EPEL). Confirmed via dry-run + smoke test. | None — ship it |
| greetd | ✅ **RESOLVED — built, installed, and verified working.** Forked from Fedora rawhide (unbranched for EPEL, not broken/unported). Needed 4 supporting crate packages forked the same way, all also just unbranched Fedora packages: `rust-pam-sys`, `rust-enquote`, `rust-greetd_ipc` (path-dep quirk in cargo2rpm's BR generation), `rust-rpassword5` (greetd's Cargo.lock pins an old major version). Real mock build succeeded, real `dnf install` succeeded, `rpm -V`/`ldd`/`greetd --help` all clean. **Confirmed the original hard blocker is gone**: `sudo dnf install --assumeno dms-greeter` now resolves cleanly end-to-end. See SETUP.md Step 11 for the full trail. | Done — upload these 6 specs to the actual COPR (see restated Goal below) |
| ghostty | Needs Zig toolchain. **Confirmed available**: `zig-0.15.2` ships from official EPEL10. Spec forked/adapted from Terra EL into `specs/ghostty/ghostty.spec` (SETUP.md Step 9). Its one dependency gap, `gtk4-layer-shell`, is now **solved and verified**: forked from Fedora rawhide, **actually mock-built successfully** in a real `centos-stream+epel-10-x86_64` chroot (SETUP.md Step 10) — real RPMs in `built-rpms/`. ghostty itself is not yet building: hit a real, diagnosed (not mysterious) Zig lazy-dependency resolution issue where its vendored `harfbuzz` C source silently fails to attach its include path under offline `--system` mode, falling back to el10's too-old system harfbuzz headers. Next step identified: vendor via a real `zig build --fetch` pass against the actual build graph (with network) rather than a flat per-URL `zig fetch` loop. | Retry ghostty vendoring via `zig build --fetch`; already unblocked on gtk4-layer-shell |
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
