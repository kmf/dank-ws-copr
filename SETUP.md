# Build Environment Setup Log — durin (CentOS Stream 10)

Reproducibility log for setting up `durin` as the DMS COPR build host.
Append new steps chronologically as we go; each entry should be copy-pasteable.

## Host
- Hostname: `durin`
- OS: CentOS Stream 10 (Coughlan), `PLATFORM_ID=platform:el10`
- User: `kmf` (member of `wheel` — has sudo)

## Step 1 — Confirm host identity
```
hostname
cat /etc/os-release
```
Confirmed CentOS Stream 10 on `durin`.

## Step 2 — Check CRB / EPEL repo state
```
sudo dnf repolist --all | grep -iE 'crb|epel|codeready'
```
Result: `epel` was **already installed and enabled**. `crb` was present but **disabled**.

## Step 3 — Enable CRB
```
sudo dnf config-manager --set-enabled crb
```
Verified with `dnf repolist --all | grep -iE 'crb|epel'` — `crb` now shows `enabled`.

Note: EPEL was already set up on this host (epel-release package already installed), so the
`dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm` step from
PLAN.md was not needed — only CRB required enabling.

## Step 4 — Refresh metadata cache
```
sudo dnf makecache
```
Observed repos already configured on this host (beyond base CentOS Stream 10 BaseOS/AppStream/CRB/Extras and EPEL):
- Copr repo: `avengemedia/danklinux`
- Copr repo: `avengemedia/dms-git`
- Copr repo: `avengemedia/dms`
- Copr repo: `yalter/niri`
- (plus unrelated personal repos: 1Password, Brave, Cider, Docker CE, insync, Tailscale — not relevant to this project)

So the "Repos to Enable on durin" list in PLAN.md is **already satisfied** except the pending
niri/Hyprland el10 chroot confirmation.

## Step 5 — Repoquery dependency tree against enabled repos
Goal: determine which PLAN.md dependencies already have packages available (via EPEL/CRB/COPR)
vs. which need a fresh port/spec.

Command pattern used:
```
dnf repoquery --available <pkgname>
```

### Tier 1 — core libs
| Package | Available? | Source (from repoquery) |
|---|---|---|
| breakpad | ✅ yes | `breakpad-2024.02.16-1.el10` (src + x86_64) |
| cli11    | ⚠️ src only | `cli11-2.6.1-1.el10.src` (no x86_64 binary listed) |
| cpptrace | ✅ yes | `cpptrace-1.0.4-4.el10` (src + x86_64) |
| matugen  | ✅ yes | `matugen-4.2.0-1.el10` (src + x86_64) |

cli11 note: no `x86_64` binary because it's a header-only library — ships as
`cli11-devel` (noarch) + `cli11-docs` (noarch). Confirmed via `dnf repoquery --available 'cli11*'`.

### Tier 2 — shell components
All fully available, prebuilt for el10, **all sourced from the same single COPR repo**:
`copr:copr.fedorainfracloud.org:avengemedia:danklinux`

| Package | Available? | Example version |
|---|---|---|
| quickshell     | ✅ yes | 0.3.1-2.el10 |
| quickshell-git | ✅ yes | 0.3.2^861.gitfae96f1-1.el10.9 |
| dgop           | ✅ yes | 1.6.2-1.el10 |
| danksearch     | ✅ yes | 1.6.0-1.el10 |
| cliphist       | ✅ yes | 0.7.0-1.el10 |
| dankcalendar-git | ✅ yes | 1.6.2+git205.c9fa860e-2.el10 (many rolling builds) |

### Tier 3 — shell packages
| Package | Available? | Source repo | Notes |
|---|---|---|---|
| dms         | ✅ yes (as git snapshots) | `copr:...avengemedia:dms-git` | See naming note below |
| dms-git     | ❌ no package by this literal name | — | Not a separate package; see note below |
| dms-greeter | ✅ yes | `copr:...avengemedia:danklinux` | 1.6.2-1.el10 |
| dms-greeter-git | ✅ yes | `copr:...avengemedia:danklinux` | rolling builds up to git50 |

**Naming note:** the binary RPM is always named `dms` (epoch 2), regardless of whether it's a
"stable" or "git" build — versions like `2:0.0.git.4850.4eb16353-1.el10` are git-snapshot builds
of the package still named `dms`. All of them come from the `avengemedia/dms-git` COPR project.
**No separate `avengemedia/dms` (stable) COPR repo is actually enabled on this host** — only
`avengemedia/dms-git` is (despite PLAN.md listing `avengemedia/dms` as a repo to enable; the
earlier `dnf makecache` metadata-refresh line for it was actually the `dms-git` repo printed under
its two Copr-generated repo ids, not a separate stable repo). **Action item:** confirm with
upstream/PLAN.md owner whether a stable `avengemedia/dms` COPR project exists at all, or whether
`dms-git` is the only channel today — this affects Open Question #2 (ship `dms` + `dms-git`, or
stable-only).

### Tier 4 — runtime alternatives
| Package | Available? | Notes |
|---|---|---|
| niri | ✅ **yes — installs cleanly** | `copr:yalter:niri`, niri-26.04-1.el10.x86_64. Dry-run (`dnf install --assumeno niri`) resolves fully against EPEL/CRB/base (only extra dep: `libseat` from EPEL). **This contradicts the PLAN.md blockers table** ("COPR doesn't install on el10") — that may be stale; re-verify before further investigation work here. |
| hyprland | ❌ no | No package in any enabled repo, incl. `lionheartp/Hyprland` (not enabled here — would need adding + checking el10 target exists) |
| mangowm | ❌ no | Not found |
| miraclewm | ❌ no | Not found (confirms PLAN.md: Mir-based, likely no el10 stack) |
| kitty | ✅ yes (from **base CentOS/EPEL**, not a Dank repo) | `kitty-0.47.1-3.el10_3.x86_64` — already packaged upstream, no porting needed |
| alacritty | ❌ no | Not found in any enabled repo |
| ghostty | ❌ no | Confirms PLAN.md: needs Zig toolchain, no prebuilt el10 package found |
| material-symbols-fonts | ✅ yes | `1.0-1.el10.noarch`, from `avengemedia/danklinux` |
| qt6ct-kde | ❌ no (as separate package) | Only plain `qt6ct-0.11-10.20250907git23a985f.el10_2` exists (no `-kde` subpackage variant found) — needs check whether KDE-style plugin is bundled in base `qt6ct` on el10 or genuinely missing |
| greetd | ❌ no | Confirmed absent — no package under this name or any `*greetd*` wildcard in any enabled repo (EPEL included). Matches PLAN.md blocker; still needs the "un-branched vs. real port" investigation |

## Summary / Findings so far
- **Tiers 1–3 (minus the `dms` stable/`dms-git` naming question) are already fully solved
  upstream** via the `avengemedia/danklinux` and `avengemedia/dms-git` COPR projects, which were
  already configured on `durin` before this session started. No net-new spec work needed there —
  just consume these repos.
- The real open packaging work is concentrated in **Tier 4**: hyprland, mangowm, alacritty,
  ghostty, greetd, qt6ct-kde have no el10 packages anywhere yet.
- **niri appears to already work on el10** (contrary to the PLAN.md blockers table) — needs a
  PLAN.md update/re-verification, not a fix.
- kitty and material-symbols-fonts need no work (kitty ships in base CentOS/EPEL already).

## Step 6 — Smoke test: dms + dms-greeter + quickshell stack

### Discovery: core stack already installed on this host
```
rpm -qa | grep -iE 'dms|quickshell|dgop|danksearch|cliphist|dankcalendar|breakpad|cli11|cpptrace|matugen'
```
Already present before this session:
- `danksearch-1.6.0-1.el10.x86_64`
- `dms-0.0.git.4850.4eb16353-1.el10.x86_64`
- `dms-cli-0.0.git.4850.4eb16353-1.el10.x86_64`
- `matugen-4.2.0-1.el10.x86_64`
- `quickshell-git-0.3.2^861.gitfae96f1-1.el10.9.x86_64`

### dms + quickshell(-git): install/integrity attempt
```
sudo dnf install --assumeno dms dms-greeter quickshell
```
Result: `quickshell` (stable) conflicts with the already-installed `quickshell-git` — expected
behavior (the two packages `Conflict`/mutually exclusive-`Provide` each other, can't have both);
**not a packaging bug**. Since `quickshell-git` is already installed and is the newer/rolling
variant, this is fine — skip stable `quickshell` on this host.

### Package integrity + runtime smoke test
```
rpm -V dms dms-cli quickshell-git matugen danksearch   # → no output = all files verified OK
ldd /usr/bin/dms | grep -i "not found"                  # → clean, no missing libs
ldd /usr/bin/dms-cli | grep -i "not found"               # → clean, no missing libs (binary path: rpm -ql dms-cli | grep bin)
ldd /usr/bin/quickshell | grep -i "not found"             # → clean, no missing libs
quickshell --version   # → "Quickshell 0.3.1 (revision fae96f1a..., distributed by Fedora COPR (avengemedia/quickshell))"
matugen --version      # → "matugen 4.2.0"
dms                     # → runs, shows cobra-style `dms [command]` usage (no --version flag, that's just this CLI's UX)
```
**Result: PASS.** `dms`, `dms-cli`, `quickshell-git`, and `matugen` are correctly installed, RPM
`-V` reports no file corruption/modification, and `ldd` shows no missing shared library
dependencies. This confirms the avengemedia COPR builds are not just present in repo metadata but
actually installable and structurally sound on this el10 host.

### dms-greeter / dms-greeter-git: BLOCKED on greetd
```
sudo dnf install --assumeno dms-greeter
sudo dnf install --assumeno dms-greeter-git
```
Both fail identically:
```
Problem: cannot install the best candidate for the job
  - nothing provides greetd needed by dms-greeter-<ver> from copr:...avengemedia:danklinux
```
Exhaustively confirmed greetd has **zero providers** in any enabled repo:
```
dnf provides greetd
dnf repoquery --whatprovides greetd
```
Both return empty against all enabled repos (BaseOS, AppStream, CRB, EPEL, all avengemedia/yalter
COPRs). This is a **hard, real blocker** — not a metadata staleness issue like the niri false-alarm
above. `dms-greeter` cannot be installed on el10 at all today until `greetd` itself is packaged.

**Status vs. PLAN.md blockers table:** confirmed as real (not stale). Next investigation step per
PLAN.md is still open: determine whether greetd is simply un-branched for EL10 in EPEL (i.e. exists
for EPEL8/9 and just needs a branch request) vs. genuinely unported. `greetd` is Rust-based
(greetd + a greeter like `tuigreet`/`regreet`), so likely blocked on the same
Rust-toolchain-on-el10 question flagged for niri/hyprland/ghostty elsewhere in PLAN.md — worth
checking as one investigation rather than four separate ones.

## Step 7 — Toolchain investigation (Rust/Zig) behind niri/hyprland/ghostty/greetd blockers

PLAN.md's blockers table assumed several Tier 4 gaps might be toolchain availability problems
(Rust for niri/greetd, Zig for ghostty) needing a "confirm buildable in mock chroot" step. Checked
directly:

```
dnf repoquery --available rust cargo zig
dnf repoquery --available --qf '%{name}-%{evr} | %{reponame}' rust cargo zig
```

| Toolchain | Available? | Source | Version |
|---|---|---|---|
| rust  | ✅ yes | **appstream** (official CentOS Stream repo, not a COPR) | 1.98.1-1.el10 |
| cargo | ✅ yes | **appstream** | 1.98.1-1.el10 |
| zig   | ✅ yes | **epel** (official EPEL10, not a COPR) | 0.15.2-2.el10_2 |

`mock-6.8-1.el10_3` is also available (not currently installed) for chroot-based builds, and
`/` has 59G free — plenty of headroom for mock build roots.

**This changes the risk assessment for three of the five PLAN.md blockers:**
- **ghostty**: the "Confirm Zig is buildable in an el10 mock chroot" step is essentially answered
  — Zig itself is an official EPEL10 package, so a mock chroot will have it available with zero
  extra setup. Remaining work is porting the spec (reference spec already linked in PLAN.md:
  `gitlab.com/lumarel/ghostty-rpm`), not toolchain bring-up.
- **greetd**: Rust is an official AppStream package. greetd is a small, all-Rust project, so the
  "not confirmed in EPEL10" blocker is **not a toolchain gap** — it's purely that nobody has
  branched/packaged it for EL10 yet. This is genuinely a from-scratch packaging job, but a low-risk
  one (no exotic build deps found — see below).
- **niri**: already confirmed working (Step 5); this just confirms *why* — its wlroots dependency
  chain is fully covered by EPEL (`wlroots-0.18.2` and `wlroots-devel` both ship from **epel**,
  official, not COPR), so Rust availability was never actually in question for niri specifically.

**hyprland gets a more precise (still real) blocker**, not resolved by this check:
```
dnf repoquery --available 'wlroots*' 'aquamarine*' 'hyprutils*' 'hyprlang*' 'hyprcursor*' 'hyprgraphics*'
```
`wlroots`/`wlroots-devel` (0.18.2, from EPEL) exist, but Hyprland's own newer dependency chain —
`aquamarine`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics` (Hyprland forked off
plain-wlroots around 0.40+) — has **zero packages** anywhere on this host. This is real porting
work (5 additional from-scratch C++/CMake specs before Hyprland itself), not a toolchain question —
these libs don't need Rust/Zig, just standard CMake/pkgconf tooling which el10 already has via
base/CRB. Moderate lift, not blocked on missing infrastructure.

### Revised blocker summary (supersedes PLAN.md's "Known Blockers" table)
| Package | Real blocker? | Root cause | Fix path |
|---|---|---|---|
| niri | ❌ not blocked | (PLAN.md entry was stale) | None — already installs cleanly today |
| ghostty | ⚠️ packaging work only | Zig toolchain now confirmed available (EPEL) | Port the linked reference spec |
| greetd | ⚠️ packaging work only | Toolchain (Rust) available; nobody has packaged/branched it for EL10 | Write a from-scratch spec (small Rust project) |
| hyprland | ⚠️ packaging work, larger | wlroots itself is fine (EPEL); Hyprland's own newer libs (aquamarine, hyprutils, hyprlang, hyprcursor, hyprgraphics) are unpackaged | Port 5 upstream libs first, then Hyprland itself — all standard CMake, no toolchain gap |
| miraclewm | ✅ still a real, deeper blocker | Mir-based, not wlroots — separate stack, not investigated further this pass | Needs its own scoping (Mir/mir-graphics-drivers availability on el10) |

**Bottom line: none of the Tier 4 gaps are blocked on missing build infrastructure** (toolchains,
mock, disk space all present/official). Every remaining gap is a "someone needs to write/port RPM
specs" problem, of varying size (greetd/ghostty = small, hyprland = larger due to its dependency
fan-out, miraclewm = unscoped).

## Step 8 — Terra EL research (not enabled on durin — research only, per explicit decision)

User suggested checking whether Terra (terra.fyralabs.com / terrapkg) already has any of our
target packages. **Not enabled on `durin`** — their documented bootstrap install uses
`--nogpgcheck` for the initial release RPM, which the session's safety guardrails correctly
flagged for explicit sign-off; user chose research-only via GitHub for now, so nothing below was
installed or verified by actually resolving against the live repo — it's spec-source research only.

### What Terra EL is
- Separate from mainline Terra (Fedora-focused): **Terra EL** is a dedicated Enterprise Linux track,
  repo `terrapkg/packages-el` on GitHub, **default branch is literally `el10`** — "Only EL10 is
  supported" per their own docs. Requires EPEL as a base.
- Documented enable command (not run): `dnf install --nogpgcheck --repofrompath 'terra,https://repos.fyralabs.com/terrael$releasever' terra-release`

### Packages found (spec-source only, confirmed present in the `el10` branch via GitHub API — NOT confirmed as actually resolvable/installable, since the repo isn't enabled)
| Package | Present in Terra EL? | Notes |
|---|---|---|
| **dank-material-shell** | ✅ yes, full spec (`anda/system/dank-material-shell/`) | Packaged as `DankMaterialShell` v1.6.1, proper Fedora-style Go spec (go-rpm-macros, systemd user unit, shell completions). **Explicitly `Obsoletes`/`Provides` `dms` and `dms-cli`** — clearly designed as a drop-in replacement/supersession of avengemedia's COPR package. Depends on `quickshell`, `cava`, `cliphist`, `danksearch`, `dgop`, `matugen`, `qt6ct`, `khal`, etc. |
| **breakpad** | ✅ yes, full spec | `anda/lib/breakpad/` |
| **ghostty** | ✅ yes — 3 channels | `anda/devs/ghostty/{stable,nightly,tip}/`, each with own spec |
| **mangowm** | ✅ yes, full spec | `anda/desktops/mangowm/mangowm.spec` — **but requires `pkgconfig(wlroots-0.19)`**, newer than the `wlroots-0.18.2` currently in EPEL10 (see Step 7), plus `scenefx-devel` (also Terra-packaged). Not a free win — has its own version-mismatch gap to resolve. |
| **hyprland's dependency libs** | ⚠️ partial | `hyprutils`, `hyprlang`, `hyprgraphics`, `hyprwayland-scanner`, `hypridle`, `hyprlock` all have specs under `anda/desktops/hyprland/`. **`aquamarine` and `hyprcursor` were not found** (GitHub code search needs auth, so this is a directory-listing check, not exhaustive). |
| **hyprland (core)** | ❌ **removed, deliberately** | Confirms/upgrades our earlier "real blocker" assessment. Terra's own removal PR (#17477) states plainly: *"they don't build anymore and we don't support hyprland as a WM, esp since the whole freedesktop thing"* — i.e. this isn't just "no el10 COPR target" (PLAN.md's original framing), it's an active third-party judgment that Hyprland is currently unbuildable/unsupportable, likely tied to Hyprland's own recent governance/licensing controversy. **Materially worse outlook than previously assessed** — worth deprioritizing rather than treating as "just needs 5 more lib ports." |
| **niri (core)** | ⚠️ not found directly | Only accessory packages present (`iio-niri`, `niri-autostart`, `nirius`) under `anda/desktops/niri/` — no `niri.spec` itself in this listing. Moot either way since niri already installs cleanly via `yalter/niri` COPR (Step 5). |
| **quickshell** | ❌ not present anywhere in Terra | Confirms `avengemedia/danklinux` COPR remains the only known source — no duplicate/competing effort to reconcile there. |

### Strategic implication — needs a decision, not just more research
Terra EL shipping a **complete, well-formed, Obsoletes-aware spec for DMS itself** changes the
shape of this project's choices. Options, roughly in order of effort:
1. **Ignore Terra, stay the current course** — keep consuming `avengemedia/danklinux` +
   `avengemedia/dms-git` COPRs as planned. Simplest, matches PLAN.md as written, but means
   duplicating packaging effort Terra has already done (and done arguably "more properly" —
   Fedora packaging conventions, Obsoletes chain, systemd user units).
2. **Adopt Terra EL as a dependency source** — enable it (after resolving the GPG-check question)
   and consume its `dank-material-shell`, `breakpad`, `ghostty` packages directly instead of
   building our own, focusing `dank-ws-copr`'s own work only on genuine gaps (greetd, and
   whatever Tier 4 pieces still aren't covered anywhere).
3. **Use Terra's specs as reference/starting points** — fork/adapt their `.spec` files (e.g. for
   ghostty, breakpad) into our own COPR rather than depending on their infra directly, keeping full
   control while not starting from zero.

This is a project-direction call, not something to decide unilaterally — flagging back to the user.

## Step 9 — Fork/adapt Terra + Fedora specs into our own repo (decision: option 3 from prior summary)

User decided: fork/adapt third-party specs into our own COPR for full control, rather than
depending on Terra's live infra or reinventing from scratch. Scope: Tier 1-3 stay on the
already-working `avengemedia` COPRs (no reason to duplicate what already works); this pass focused
on the two most tractable Tier 4 gaps — **ghostty** and **mangowm** — plus whatever they needed.

### Vendored so far (under `specs/` in this repo, see `specs/NOTICE.md` for attribution)
- `specs/ghostty/ghostty.spec` — forked from Terra EL, adapted:
  - Dropped `anda-srpm-macros` (Terra/Anda build-system-specific, not available/needed here)
  - `zig0.15` -> `zig` (el10's EPEL ships a single current `zig` package; Terra versions it separately)
  - Rewrote `%install` to use the official EPEL10 `zig-rpm-macros` package's `%zig_install` macro
    (verified its macro definitions via `rpm -ql zig-rpm-macros` / `/usr/lib/rpm/macros.d/macros.zig`)
    instead of Terra's Anda-only `%{zig_build_target}`, translating release-mode/flags as closely
    as possible to the original invocation.
  - **Real gap found**: `pkgconfig(gtk4-layer-shell-0)` — confirmed absent from every enabled repo
    (checked EPEL/CRB/base/all COPRs) and absent from Terra EL too (they don't package it either,
    at least not yet in the `el10` branch).
- `specs/gtk4-layer-shell/gtk4-layer-shell.spec` — forked from **Fedora's own rawhide dist-git**
  (not Terra — Terra doesn't have it), to unblock ghostty. Adapted: replaced `%autorelease`/
  `%autochangelog` (Fedora's rpmautospec tooling, not installed here — checked, `rpmautospec-rpm-macros`
  missing) with a static `Release: 1%{?dist}` and manual changelog entry.
  **Every other build dependency checked and confirmed present on el10**: `gcc`, `meson`, `vala`,
  `gobject-introspection-devel`, `gtk4-devel`, `wayland-devel`, `wayland-protocols-devel`,
  `python3-gobject`. This looks like a clean, low-risk port with nothing else in the way.
- `specs/mangowm/mangowm.spec` — forked **verbatim, not adapted** from Terra EL; kept as reference
  only. **Deprioritized**: needs `pkgconfig(wlroots-0.19)` (el10's EPEL only has 0.18.2) — checked
  whether Terra EL packages a newer wlroots themselves (`anda/lib/` listing) and **they don't
  either**, meaning this spec may not even be buildable within Terra's own repo, not just ours.
  Also needs `scenefx-devel`, which Terra *does* package (not yet ported here). Building a newer
  wlroots ourselves risks colliding with the 0.18.2 that `niri` and other consumers already use on
  this host — real engineering risk, not just missing-spec busywork. Sequenced below ghostty.

### Also checked this pass
- `layer-shell-qt` exists on el10 (Qt's own layer-shell binding) — unrelated to GTK's, doesn't help.
- No `gtk-layer-shell` (GTK3 variant) exists on el10 either, in case that was a smaller first step —
  it isn't smaller, both are equally unported; went straight for the GTK4 one ghostty actually needs.

### Not yet done (deliberately out of scope this pass)
- No mock build attempted yet for either adapted spec — `mock` package is available but not
  installed on `durin` (see Step 7). Installing it and doing a real `mock -r <el10 config>`
  build of `gtk4-layer-shell` then `ghostty` is the natural next verification step, since both
  spec adaptations above are informed-but-unverified translations, not tested output.
- Hyprland's dependency libs (`hyprutils`, `hyprlang`, `hyprgraphics`, etc., which Terra does carry
  specs for) were not forked this pass, since Hyprland core itself is deprioritized (Step 8) — no
  point porting libraries for a compositor we're not currently planning to ship.
- `breakpad` and `dank-material-shell` specs exist in Terra too but were **not** forked — Tier 1-3
  already work via `avengemedia` COPRs and don't need a second implementation.

## Step 10 — Install mock, real builds: gtk4-layer-shell (SUCCESS) and ghostty (blocked, root cause identified)

### Mock setup
```
sudo dnf install -y mock
sudo usermod -aG mock kmf        # takes effect via `sg mock -c "..."` this session, new login otherwise
sudo dnf install -y rpmdevtools rpm-build createrepo_c
rpmdev-setuptree
```
Used the built-in `centos-stream+epel-10-x86_64` mock config (ships with `mock-core-configs`) —
exactly CentOS Stream 10 + EPEL, matching our target.

Confirmed along the way: `rpmautospec-rpm-macros` genuinely does not exist on el10 (only the
unrelated `python3-rpmautospec` CLI tool does) — so the earlier decision to drop `%autorelease`/
`%autochangelog` from the gtk4-layer-shell spec was correct and necessary, not just a guess.

**Gotcha hit immediately**: RPM expands `%macro`-looking text even inside `#` comments. The
attribution headers added to the vendored specs in Step 9 used bare `%autorelease`, `%prep`,
`%install` etc. in prose, which broke spec parsing (`Unknown option > in autorelease`). Fixed by
escaping every such reference as `%%` in `specs/ghostty/ghostty.spec` and
`specs/gtk4-layer-shell/gtk4-layer-shell.spec` (mangowm's header had none, unaffected). Also caught
a wrong weekday in a manual `%changelog` entry (`Wed Sep 24 2026` — actually a Thursday); RPM
warns but doesn't fail on that, fixed anyway.

### gtk4-layer-shell: ✅ built successfully, real artifacts produced
```
cd ~/rpmbuild/SPECS && spectool -g -R gtk4-layer-shell.spec   # downloads Source0 tarball
rpmbuild -bs gtk4-layer-shell.spec                             # -> SRPM
sg mock -c "mock -r centos-stream+epel-10-x86_64 --rebuild <srpm>"
```
Result: clean build, no errors. Produced `gtk4-layer-shell-1.3.0-1.el10.x86_64.rpm`,
`-devel`, `-debuginfo`, `-debugsource` — all copied into `built-rpms/` in this repo (gitignored,
not committed — binary build output, not source). Installed the `-devel` package locally and
confirmed `pkg-config --modversion gtk4-layer-shell-0` → `1.3.0`. **This genuinely unblocks
ghostty's missing dependency** — verified, not just theorized.

### ghostty: real progress, but blocked on a Zig lazy-dependency nuance — not yet building
Iterative debugging, each step a real build failure diagnosed and fixed:

1. **First real failure**: `%prep`'s `./nix/build-support/fetch-zig-cache.sh` tries to
   `git fetch`/download ~34 Zig package dependencies (listed in upstream's `build.zig.zon.txt`)
   over the network. Mock (like real COPR builds) disables network during `%build`/`%prep` by
   design. Fixed by vendoring: ran `zig fetch <url>` for all 34 URLs *outside* mock (real network),
   producing a 559MB cache, tarred as `ghostty-1.3.1-zig-vendor.tar.zst` (75MB compressed, kept
   locally in `built-rpms/`, gitignored — not yet uploaded anywhere permanent, see below), added as
   `Source2`, and rewrote `%prep` to extract it instead of running the fetch script.
2. **Second failure**: `error: unable to open system package directory '.../zig-cache/p': FileNotFound`.
   Cause: I'd kept Terra's original `mv "%{_zig_cache_dir}/p" "zig-pkg"` line, which was specific to
   their own Anda-only `%{zig_build_target}` macro's expectations. The *official* `zig-rpm-macros`
   `%zig_install` macro expects the fetched-package directory to stay named `p` (via
   `_zig_package_dir = _zig_cache_dir/p`, see `/usr/lib/rpm/macros.d/macros.zig`). Removed the `mv`.
3. **Third failure** (real compile error, build actually started compiling C/C++ this time):
   `pkg/harfbuzz/buffer.zig:292: error: ... has no member named 'HB_BUFFER_CLUSTER_LEVEL_GRAPHEMES'`.
   Root cause: el10's system `harfbuzz-devel` is 8.4.0; ghostty's Zig bindings expect the newer API
   from the harfbuzz it vendors itself (11.0.0). Ghostty defaults to *preferring system libraries*
   on Linux (`b.systemIntegrationOption(...)`, default `null` -> effectively "system" on non-macOS).
   Traced Zig's build-runner source (`/usr/lib/zig/compiler/build_runner.zig`) to find the actual
   flag: `-fno-sys=<name>` forces building the vendored copy instead. Added
   `%global zig_build_options -fno-sys=harfbuzz` to force the vendored harfbuzz.
4. **Fourth failure — same error persists**, even with `-fno-sys=harfbuzz` confirmed present in the
   actual invocation line in the build log. Traced through ghostty's own
   `pkg/harfbuzz/build.zig`/`build.zig.zon`/`c.zig` source on GitHub to find why: the vendored
   harfbuzz C source is pulled in via `b.lazyDependency("harfbuzz", .{})` — and it's declared
   `.lazy = true` in `pkg/harfbuzz/build.zig.zon`. When that call returns `null` (which it appears
   to, here), the `if (b.lazyDependency(...)) |upstream| { module.addIncludePath(upstream.path("src")); ... }`
   block that would add the *vendored* header search path is silently skipped entirely — so
   `c.zig`'s `@cInclude("hb.h")` falls through to default system include paths and finds the old
   system header regardless of the link-mode flag. **This is a Zig lazy-dependency resolution
   quirk under `--system <dir>` offline mode**, not a simple spec bug: our vendoring approach (a
   flat `zig fetch <url>` loop over every URL in `build.zig.zon.txt`) populates the content-addressed
   cache by hash, but doesn't reproduce whatever internal state make `lazyDependency` return non-null
   during an offline `--system`-mode build.

**STATUS: not resolved this session.** Real, concrete next step (not attempted yet, stopped here to
report rather than keep guessing blind): try vendoring via an actual `zig build --fetch` pass run
directly against ghostty's real build graph *with real network access* (rather than a flat per-URL
loop against `build.zig.zon.txt`), since that is the mechanism that's supposed to force-materialize
every reachable lazy dependency the way a real (non-`--system`) build would. Then re-tar whatever
cache state that produces and re-test in mock. This is well-diagnosed, not mysterious — just not
finished.

### greetd: status (user asked directly)
Per PLAN.md's original open question ("un-branched vs. real port"), checked directly:
- **Confirmed via Fedora dist-git branch listing**: `greetd.spec` exists at `rawhide`, `f41`, `f42`
  (HTTP 200) but **404s at both `epel9` and `epel10`** — i.e., genuinely never branched to any EPEL
  release, not a removed/broken package. This is the "just un-branched" case, the good outcome.
- Fetched the Fedora rawhide spec and checked every `BuildRequires`: `cargo-rpm-macros` (from
  **EPEL**, not even needing CRB), `make`, `scdoc`, `sed`, `systemd-rpm-macros`,
  `selinux-policy-devel` — **all present on el10**.
- Spec uses Rust's vendored-crate packaging convention (`%cargo_prep`, `%generate_buildrequires` +
  `%cargo_generate_buildrequires`, reading `Cargo.lock`). Checked greetd's actual crate
  dependencies (`nix`, `pam-sys`, `serde`, `serde_json`, `libc`, `tokio`, `getopts`, `thiserror`,
  `async-trait`, `enquote`, `rpassword`) against el10's individually-packaged `rust-*-devel` crates
  (Fedora's `rust2rpm` auto-packages these, and EPEL/AppStream carry a large slice of the common
  ecosystem already): **9 of 11 already exist** as packages. Only **`pam-sys`** and **`enquote`**
  are missing — both small, standalone leaf crates, not application-sized ports.
- **Conclusion: greetd is not the open-ended "real port" PLAN.md worried about.** It's the
  un-branched case, the spec is clean, and it's genuinely close — nearest to gtk4-layer-shell in
  difficulty (a couple of small crate packages away), likely easier than ghostty's remaining
  lazy-dependency issue. **Not yet forked into `specs/` or attempted in mock this session** — next
  candidate for the same treatment gtk4-layer-shell got.

## Step 11 — greetd: forked, built, installed, verified — full end-to-end success

Followed the exact same fork-from-Fedora-rawhide pattern as gtk4-layer-shell (Step 10), but hit two
more real dependency gaps along the way, each resolved the same way: check if Fedora already has a
spec for it (it did, both times), fork, adapt, build, retry.

### Attempt 1: greetd alone -> 4 unmet crate requirements
```
sg mock -c "mock -r centos-stream+epel-10-x86_64 --addrepo=file:///.../built-rpms --rebuild greetd-0.10.3-1.el10.src.rpm"
```
`%generate_buildrequires`/`%cargo_generate_buildrequires` (dynamic BR resolution against the real
Cargo.lock) failed with:
```
Problem 1-3: nothing provides crate(greetd_ipc/{default,sync-codec,tokio-codec}) ...
Problem 4: nothing provides crate(rpassword/default) >= 5.0.0 with < 6.0.0
```
Two genuinely new gaps, not the `pam-sys`/`enquote` ones from Step 10 (those resolved cleanly this
time - confirms the earlier fork worked):
- **`greetd_ipc`**: greetd's own `Cargo.toml` uses a local *path* dependency
  (`{ path = "../greetd_ipc" }`, same source tree) for this, but `cargo2rpm`'s BR generator still
  emits an external `crate(greetd_ipc/...)` requirement regardless of path-vs-registry origin.
  Checked whether Fedora's own greetd build has the same issue: it does, and solves it with a
  **separate `rust-greetd_ipc` package** (real, because `greetd_ipc` is independently published on
  crates.io too, so rust2rpm can auto-generate a spec for it).
- **`rpassword`**: extracted the *actual* release tarball (not GitHub's live `master`, which could
  drift from the tagged release) and checked `Cargo.lock` directly: pins `rpassword = 5.0.1` exactly.
  el10 only has `rust-rpassword` 7.5.4 (EPEL) - a semver-incompatible major bump. Checked how
  Fedora's own build handles it: a **`rust-rpassword5` compat package** (side-by-side-installable
  by design, already branched to epel9, just not epel10 yet - an established pattern, not exotic).

(Also checked whether `nix` would hit the same issue - Cargo.lock pins `0.27.1`, el10 only has
`0.31.3`, a 0.x "different minor = incompatible" situation by Cargo's semver rules - but the solver
did NOT flag it as unmet, so left it alone rather than fixing a non-problem.)

### Forked two more packages, same treatment as before
- `specs/rust-greetd_ipc/rust-greetd_ipc.spec` - forked from Fedora rawhide (404 on epel9/epel10),
  adapted (`%autorelease`/`%autochangelog` -> static). Built clean in mock, first try.
- `specs/rust-rpassword5/rust-rpassword5.spec` + its `rpassword-fix-metadata-auto.diff` patch -
  forked from Fedora rawhide (branched to epel9, not epel10), same adaptation. Built clean in mock,
  first try.

### Attempt 2: greetd with all four crates available -> SUCCESS
```
createrepo_c --update built-rpms/    # after copying in the two new crate RPMs
sg mock -c "mock -r centos-stream+epel-10-x86_64 --addrepo=file:///.../built-rpms --rebuild greetd-0.10.3-1.el10.src.rpm"
```
**`INFO: Done`, no errors.** Produced `greetd`, `greetd-selinux`, `greetd-fakegreet`,
`-debuginfo`/`-debugsource` - all in `built-rpms/` (gitignored, not committed).

### Full smoke test - real install, not just a build
```
sudo dnf install -y built-rpms/greetd-0.10.3-1.el10.x86_64.rpm built-rpms/greetd-selinux-0.10.3-1.el10.noarch.rpm
rpm -V greetd greetd-selinux        # -> clean, no output
ldd /usr/bin/greetd | grep "not found"    # -> clean
ldd /usr/bin/agreety | grep "not found"   # -> clean
greetd --help                              # -> works
rpm -q --provides greetd | grep service    # -> service(graphical-login) = greetd
```
Installed cleanly (sysusers-based `greetd` user/group creation produced harmless ordering warnings
during the scriptlet, self-resolved immediately after - not a real problem).

**Confirmed the original blocker is completely gone**:
```
sudo dnf install --assumeno dms-greeter
# -> Dependencies resolved. Installing: dms-greeter 1:1.6.2-1.el10 ... (no errors)
```
This was the exact `nothing provides greetd` failure from the very start of this session (see
Step 6). **It's fully resolved now** - `dms-greeter`/`dms-greeter-git` can install today given these
5 forked packages (`greetd`, `greetd-selinux` as its subpackage, `rust-greetd_ipc`,
`rust-rpassword5`, plus the earlier `rust-pam-sys`/`rust-enquote`).

### Package count summary for this thread of work
6 new specs forked and verified-buildable this session: `gtk4-layer-shell`, `rust-pam-sys`,
`rust-enquote`, `rust-greetd_ipc`, `rust-rpassword5`, `greetd`. All under `specs/` with attribution
headers; none uploaded to any actual COPR yet (see PLAN.md's restated goal below).

## Step 12 — Push to GitHub, install copr-cli

User confirmed the `kmf/dank-ws-copr` GitHub repo exists. This host had no `gh` auth and no git
remote configured yet.
```
gh auth status                          # -> not logged in
ssh -T git@github.com                   # -> "Host key verification failed" (fresh known_hosts)
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
ssh -T git@github.com                   # -> "Hi kmf! ... successfully authenticated"
git remote add origin git@github.com:kmf/dank-ws-copr.git
git fetch origin                        # -> confirmed genuinely empty, no branches, safe to push
git push -u origin main
```
Pushed clean — confirmed via `curl https://api.github.com/repos/kmf/dank-ws-copr`: public repo,
default branch `main`, all 5 local commits present. Live at https://github.com/kmf/dank-ws-copr.

Also installed `copr-cli` (`sudo dnf install -y copr-cli`) in preparation for creating the actual
COPR project. **Blocked on a manual step**: it needs an API token tied to a Fedora Account
(generate at copr.fedorainfracloud.org/api/ while logged in, save to `~/.config/copr`) — this
can't be generated from here, it's tied to your own Fedora account/browser session.

## Step 13 — ghostty: the Zig lazy-dependency issue, fully solved

Picked up exactly where Step 10 left off: `harfbuzz` (a *nested* lazy dependency, declared inside
ghostty's own `pkg/harfbuzz/build.zig.zon`, not the project root) silently failed to get its
vendored include path attached under mock's offline `--system` mode, falling back to el10's
too-old system `harfbuzz-devel` headers.

### Ruling out `zig build --fetch` as the vendoring mechanism
Tried `zig build --fetch` directly against ghostty's real build graph (the theory: it should
"properly" walk lazy deps, unlike a flat per-URL loop). Result: only fetched 5.4MB, vs. 559MB from
the flat-loop approach — confirms upstream's own `fetch-zig-cache.sh` comment
("`zig build --fetch` doesn't fetch transitive dependencies... A future Zig version will hopefully
fix" this) is accurate. The flat per-URL loop was already the *right* approach; abandoned this path.

### Isolating the real root cause
Extracted the actual `ghostty-1.3.1.tar.gz`, and ran a real, **network-enabled, non-`--system`**
`zig build install` locally (installing all real BuildRequires by hand first). **It succeeded
completely** — produced a working `ghostty` binary, with harfbuzz correctly built from vendored
11.0.0 source (confirmed: the actual `zig build-lib` invocation line included
`-I <cache>/p/<harfbuzz-hash>/src`).

This proved the vendor tarball/cache content was never the problem. Re-ran the *exact same* build,
adding only `--system <cache>/p` (network still available) - **reproduced the identical harfbuzz
error immediately**. This cleanly isolates the cause to Zig 0.15.2's `--system` flag itself, not
missing files, not our spec, not the vendoring approach.

Tried patching the nested `pkg/harfbuzz/build.zig.zon`'s `.lazy = true` -> `.lazy = false` (theory:
laziness itself was the issue) - **no change**, ruled out.

### The actual mechanism, empirically confirmed
Uninstalled `harfbuzz-devel` from the host entirely and re-ran the same `--system`-mode build:
**the harfbuzz error vanished immediately**, replaced only by unrelated "package not installed"
errors from other things collaterally removed. Reinstalling everything *except* re-testing with
all six of ghostty's optional "system-preferred" C dependencies
(`harfbuzz`/`freetype`/`fontconfig`/`libpng`/`zlib`/`oniguruma` - the exact list in ghostty's own
`src/build/Config.zig`) explicitly forced to vendored via `-fno-sys=<name>` for *all six*, not just
`harfbuzz` alone, produced a **clean, complete, 186/186-step successful build** under `--system`
mode, with a working `ghostty --version` binary.

**Root cause, precisely**: outside `--system` mode, all six of these dependencies default to
vendored automatically (their shared default is `b.graph.system_package_mode`, which is only
`true` when `--system` is passed). A plain build with only `-fno-sys=harfbuzz` "works" in that
case because the other five were *already* going to be vendored regardless. Under `--system` mode,
all six flip their *default* to "prefer system" - so forcing only harfbuzz off system while leaving
the other five on their new (system-preferring) default reproduces a different-but-confusingly-
identical-looking cimport failure, because ghostty's own harfbuzz Zig module transitively imports
`freetype.zig` (see `pkg/harfbuzz/build.zig`'s `.imports = &.{ ... freetype ... }`), so a
freetype system/vendored mismatch cascades into a harfbuzz-attributed error. The fix is to pass
`-fno-sys=` for the full set, replicating the known-good non-`--system` default configuration
exactly, not just the one dependency the error message happened to name.

### Applied to the spec, verified in real mock
- `specs/ghostty/ghostty.spec` `%install`: `zig_build_options` now passes
  `-fno-sys=harfbuzz -fno-sys=freetype -fno-sys=fontconfig -fno-sys=libpng -fno-sys=zlib -fno-sys=oniguruma`
  (was just `-fno-sys=harfbuzz`).
- Kept `BuildRequires: pkgconfig(harfbuzz)` (tried removing it first as an alternate fix - doesn't
  help, since `gtk4-devel` -> `pango-devel` already `Requires: pkgconfig(harfbuzz) >= 2.6.0`
  transitively, so it's unconditionally present in the chroot regardless of our own declaration).
- **New, separate bug found and fixed along the way**: `%{evr}` (used throughout the spec's
  `Requires:`/`Obsoletes:` lines, e.g. `Requires: %{name}-terminfo = %{evr}`) is **not a defined
  RPM macro on el10** - confirmed via `rpm --eval '%%{evr}'` echoing the literal text back
  unchanged. It's a newer Fedora-only convenience macro not yet in el10's `redhat-rpm-config`. The
  "Possible unexpanded macro" warnings rpmbuild had been printing on every use of `%{evr}` since
  this spec was first forked (Step 9) turned out to be **real, not cosmetic** - it silently baked
  the literal string `%{evr}` into the built RPM's dependency metadata, making every subpackage
  genuinely uninstallable (`nothing provides ghostty-terminfo = %{evr}`). Fixed with one line:
  `%global evr %{version}-%{release}` right after `Release:` - resolves every use throughout the
  spec without touching them individually.

### Final verification - real build, real install, real smoke test
```
sg mock -c "mock -r centos-stream+epel-10-x86_64 --addrepo=file:///.../built-rpms --rebuild ghostty-1.3.1-3.el10.src.rpm"
# INFO: Done
sudo dnf install -y built-rpms/ghostty-1.3.1-3.el10.x86_64.rpm built-rpms/ghostty-terminfo-1.3.1-3.el10.noarch.rpm
rpm -V ghostty ghostty-terminfo    # -> clean
ldd /usr/bin/ghostty | grep "not found"    # -> clean
ghostty --version
# Ghostty 1.3.1 / channel: stable / Zig 0.15.2 / GTK 4.20.3 / libadwaita 1.8.4 / ...
```
**ghostty is now fully resolved** - built, installed, verified. 17 RPMs produced (main package,
`-terminfo`, `-devel`, shell completions for bash/fish/zsh, `-vim`/`-neovim`/`-kio`/`-nautilus`/
`-bat-syntax`/`-shell-integration`, `libghostty-vt` + `-devel`, plus debuginfo/debugsource). This is
the 7th verified-working spec this session, and resolves the last open Tier 4 blocker that wasn't
either a hard external gap (miraclewm) or a deliberate deprioritization (hyprland).

## Step 14 — mangowm investigation: wlroots0.19 + scenefx built, mangowm itself blocked on a version-drift discovery

Followed the same fork-from-Fedora pattern for mangowm's two known gaps (Step 9): `wlroots-0.19`
and `scenefx-devel`.

### wlroots0.19: forked from Fedora rawhide, built clean first try
Full dependency sweep against el10 before forking (`libliftoff`, `egl`, `gbm`, `glesv2`, `hwdata`,
`lcms2`, `libdisplay-info`, `libdrm`, `libinput`, `libseat`, `libudev`, `pixman-1`, `vulkan`,
`wayland-*`, all the `xcb-*` variants, `xkbcommon`, `xwayland`) - all present. Deliberately did NOT
use Fedora's current unversioned `wlroots` (0.20.2) instead: checked its BuildRequires too and
found real version floors above what el10 ships (`pixman-1 >=0.46.0` vs el10's 0.43.x,
`wayland-protocols >=1.47` vs 1.41, `xkbcommon >=1.8.0` vs 1.7.0, `libdisplay-info >=0.2.0` vs
0.1.1) - a bigger, riskier cascade, and `wlroots0.19` cleanly matched el10 as-is. Forked, adapted
(`%autorelease`→static, per the usual pattern), built clean in mock on the first try.

### scenefx: Fedora's current spec targets the wrong wlroots - had to go find an older release
Fedora's rawhide/f44/f45 `scenefx.spec` is all version 0.5, requiring `pkgconfig(wlroots-0.20)` -
no 0.19-compatible version left anywhere in Fedora. Checked upstream's own GitHub tags/meson.build
history directly: **0.4.1** is the last release whose `meson.build` targets `wlroots-0.19`
specifically (`wlroots_version = ['>=0.19.0', '<0.20.0']`). Wrote a spec from scratch (not
machine-adapted from Fedora's, since the version differs) following Fedora's packaging structure/
conventions, pinned to 0.4.1. **Caught one real bug before building**: scenefx's meson.build names
its versioned library/pkgconfig/include-dir after **major.minor only**
(`scenefx-0.4`), not the full version - Fedora's 0.5 spec gets away with using `%{version}` because
0.5 has no patch component, but our 0.4.1 does, so a naive copy would have shipped
`libscenefx-0.4.1.so` in `%files` while the actual build output is `libscenefx-0.4.so` -
`%files` would have failed the build for using the wrong path (`Installed (but unpackaged)
file(s) found` / missing file, one or the other). Fixed with a `%global soname_ver 0.4` before
writing the spec, verified against 0.4.1's actual meson.build content on GitHub, not assumed. Built
clean in mock on the first try once the local `wlroots0.19` repo was in place.

### mangowm itself: real build attempt, hit a genuine version-drift discovery
Built the SRPM and ran it through mock with `wlroots0.19` + `scenefx` available. Failed with:
```
Run-time dependency wlroots-0.20 found: NO (tried pkgconfig)
meson.build:33:14: ERROR: Dependency "wlroots-0.20" not found, tried pkgconfig
```
**mango's own source at the exact 0.16.3 tag Terra's spec pins already requires wlroots-0.20**,
contradicting Terra's own `BuildRequires: pkgconfig(wlroots-0.19)` line - their spec had simply gone
stale relative to upstream's own version churn (mango moves fast: tags run 0.14.0 through current
0.17.3). Bisected via GitHub raw `meson.build` fetches across tags to find exactly where the
requirement changed: **0.14.0 is the last mango release still targeting wlroots-0.19**; 0.15.0
onward all require wlroots-0.20.

Re-checked the wlroots-0.20 version floors more carefully (picking the *latest available* el10
package each time, not just the first listed - `libdrm` had already surprised me this way once
this session): **2 of the original 4 flagged mismatches turned out to already be resolved** -
`wayland-protocols-devel` has 1.49 available (needed >=1.47) and `libdisplay-info-devel` has 0.2.0
available (needed >=0.2.0), both just weren't the *first* result `dnf repoquery` printed. Only
**`pixman-devel`** (latest available 0.43.4, needed >=0.46.0) and **`libxkbcommon-devel`** (latest
available 1.7.0, needed >=1.8.0) are genuine remaining gaps - and unlike `wlroots`, these can't get
a side-by-side compat package cleanly, since wlroots/mango reference them by their plain,
unversioned pkgconfig names (`pixman-1`, `xkbcommon`), not a versioned one like `wlroots-0.19` vs
`wlroots-0.20`.

**Presented this as a real fork-in-the-road decision rather than picking unilaterally** (system-wide
library bump vs. an old pinned mango vs. deprioritizing) - **user decided: bump pixman + xkbcommon
system-wide.** Not yet executed as of this write-up. Doing so means: fork/build newer `pixman` and
`xkbcommon`, fork/build Fedora's current unversioned `wlroots` (0.20.2), re-point `scenefx` back to
its current 0.5 release (targeting wlroots-0.20, not the 0.4.1 we just built), then retry `mangowm`
0.16.3 itself. The already-built `wlroots0.19`/`scenefx-0.4.1` pair remains valid, verified work -
just not the path mangowm ends up using; may still be useful later as a stable/older base for
something else.

**Also recorded standing preference (explicit, 2026-09-24): always prefer `avengemedia` over Terra
(or any other third-party source) when both provide equivalent packages.** Settles the earlier
"build vs. adopt Terra's DankMaterialShell spec" open question for good - stick with avengemedia's
`dms`/`dms-cli`. See PLAN.md's Related Links section for the full note.

## Step 15 — Hyprland dependency chain: 6 more libs forked, built, verified

User asked to build hyprland and miraclewm next. Started with hyprland's dependency chain, since
core `hyprland`/`aquamarine` need from-scratch specs (neither Terra nor Fedora has ever packaged
`aquamarine`; Terra's `hyprland` directory is now fully deleted with no history easily recovered -
checked their removal PR #17477, which only removed leftover dependency-lib variants, not
`hyprland.spec`/`aquamarine.spec` themselves, meaning those may never have existed in this repo).

Checked Fedora dist-git for the six libs previously identified (Step 8) as at least partially
covered by Terra: `hyprwayland-scanner`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics` all
exist in Fedora rawhide (none branched to epel9/epel10 - same unbranched pattern as everything else
this session). Forked all five, plus discovered and forked a sixth, transitively-needed dependency:
**`libspng`** (hyprgraphics needs `pkgconfig(spng)`, absent from el10 entirely).

All six built clean in mock, in dependency order (`hyprwayland-scanner`/`hyprutils`/`libspng` have
no internal deps → `hyprlang` needs `hyprutils` → `hyprcursor`/`hyprgraphics` need `hyprlang`):
- `hyprwayland-scanner` 0.4.2 - clean first try.
- `hyprutils` 0.7.1 - clean first try.
- `libspng` 0.7.4 - **one real failure, fixed**: Fedora's spec patches two test cases
  (`ch1n3p04`/`ch2n3p08`) to `should_fail: true`, working around spng's incompatibility with
  libpng >=1.6.47's PNGv3 behavior change. El10's libpng is 1.6.40 (predates that change), so
  applying Fedora's patch caused the *opposite* problem - those two tests **unexpectedly passed**,
  which `meson test`/`%check` treats as a failure too. Fix: drop that sed patch entirely (confirmed
  via a real failed build first, not assumed).
- `hyprlang` 0.6.4 - clean first try (against the local `hyprutils`).
- `hyprcursor` 0.1.11 - clean first try, once its test-data source was sorted: Fedora's spec
  references `Source: HyprBibataModernClassicSVG.tar.gz` with no URL (lives in Fedora's lookaside
  cache, not a plain public link) - resolved via
  `https://src.fedoraproject.org/lookaside/pkgs/hyprcursor/HyprBibataModernClassicSVG.tar.gz/sha512/<hash>/...`
  (hash from Fedora's package `sources` metadata file) and vendored directly.
- `hyprgraphics` 0.1.5 - clean first try, once `libspng` was in place. Disabled its optional
  `libjxl` bcond (not needed for hyprland itself; avoids porting `libjxl`/`libjxl_cms`/
  `libjxl_threads` too, which weren't checked/needed for anything else this session).

### Full chain installs and resolves together
```
sudo dnf install -y hyprutils hyprlang hyprcursor hyprgraphics hyprwayland-scanner-devel libspng
# Complete! - pulls in tomlplusplus, pugixml, libzip transitively from el10/EPEL, no conflicts
rpm -V hyprutils hyprlang hyprcursor hyprgraphics hyprwayland-scanner-devel libspng   # -> clean
```

### Remaining for hyprland itself
Two packages need genuinely from-scratch specs, no reference anywhere found (checked Fedora dist-git
and both Terra repos): **`aquamarine`** (Hyprland's own rendering/backend library, replaced direct
wlroots usage since Hyprland 0.40+) and **`hyprland`** itself. Both projects are actively maintained
upstream with recent releases (Hyprland v0.56.2, Aug 2026; aquamarine v0.15.1, Sep 2026) - Terra's
stated reason for dropping support ("doesn't build anymore... whole freedesktop thing") may be
specific to their own build environment/policy rather than a universal breakage, worth still
attempting rather than treating as a hard stop. `hypridle`/`hyprlock` (optional utilities, Terra
had specs for both before deletion, not yet recovered) are lower priority than core `hyprland`.

## Step 16 — Correcting the miraclewm research error; mir + miracle-wm forked

User caught a real mistake: the earlier miraclewm assessment ("needs the entire Mir toolkit, none
of which exists anywhere") was based on checking the wrong Fedora dist-git package names
(`miraclewm`, `mir-libs`, `miral`, `mircommon` as separate repos - all genuinely 404, but not
because they don't exist, because they're not how Fedora names things here).

Correct names: **`mir`** (a single 694-line spec building `miral`/`mircommon`/`mirplatform`/
`mirserver`/`mirwayland`/etc. as subpackages of one SRPM, currently 2.29.0, updated Sep 21 2026) and
**`miracle-wm`** (hyphenated, currently 0.11.0, also updated Sep 21 2026 - and there's an official
Fedora Spin built around it). Both genuinely real, actively-maintained Fedora packages. Neither
branched to epel9/epel10 (checked, same unbranched pattern as everything else this session).

Full BuildRequires sweep for `mir` against el10 turned up a remarkably close match - including
fairly niche packages already present (`wlcs` the Wayland conformance test suite, `glm-devel`,
`gflags-devel`, `lttng-ust-devel`, `umockdev` itself is even there... wait, checked again: only
`pkgconfig(umockdev-1.0)` and `python3-dbusmock` are missing, both used only by `%check` (gtest
mocking helpers for Mir's own test suite). Fixed by flipping `mir`'s own `%bcond run_tests 1` ->
`0` rather than trying to package two more test-only dependencies.

`miracle-wm`'s own BuildRequires (beyond the `mir` subpackages) - `json-c`, `libnotify`,
`nlohmann_json`, `pcre2`, `gtk4`, `gtk4-layer-shell-0` (already built earlier this session for
ghostty) - all present or already ours.

Neither spec needed `%autorelease`/`%{evr}` fixes - both already use static `Release: 1%{?dist}`.
Forked both as-is (mir) or near-as-is; `mir`'s SRPM built cleanly, mock build kicked off (large,
mixed C++/Rust codebase using cargo-rpm-macros for an input-evdev-rs component - real size, running
in the background while other work continued in parallel chroots via `--uniqueext`).

## Step 17 — hyprland's remaining gaps: xkbcommon/lua bumps, muparser from scratch

Continuing hyprland per the user's "continue through all of it" decision, in parallel with the
`mir` build (using `mock --uniqueext=<name>` to run independent chroot instances concurrently
without lock contention - confirmed mock serializes same-named chroots, `--uniqueext` sidesteps it).

- **`libxkbcommon`**: assumed this needed a real, standalone version bump investigation - turned out
  Fedora rawhide is already at 1.13.1 (>= hyprland's required 1.11.0), unmodified fork. **This
  REPLACES el10's system libxkbcommon** (1.7.0 -> 1.13.1) rather than a side-by-side compat package,
  since it's referenced by its plain unversioned pkgconfig name everywhere (niri, mir, hyprland) -
  the system-wide-bump path the user already approved for mangowm's pixman/xkbcommon situation.
  Built clean in mock, first try.
- **`muparser`**: genuinely no distro reference spec found anywhere (checked Fedora rawhide/epel,
  404). Used openSUSE's official `science/muparser` OBS spec as a *structural* reference (fetched
  via OBS's public source API) but rewrote it in Fedora/el style rather than copying their
  soname-versioned package-naming convention (`libmuparser2_3_5`) or their unavailable
  `muparser-abiversion.diff` patch - not needed, hyprland just wants a plain `pkgconfig(muparser)`.
  Built clean in mock, first try.
- **`lua`**: initially assumed this needed a from-scratch spec too (checked `lua5.5`/`lua-5.5`/
  `lua55` as separate package names, all 404) - Fedora's actual package is simply named `lua`
  (unversioned) and had *already* been bumped to track 5.5.1. This is the most structurally complex
  fork this session: an autotools-based build with a live bootstrap flow (builds both the target
  5.5.1 *and* a compat 5.4.9 library), 6 patches, and 2 small local source files (`mit.txt`,
  `luaconf.h`) fetched directly from Fedora's git tree rather than lookaside. Forked verbatim,
  trusting Fedora's working recipe rather than trying to simplify a build this hacky. SRPM built
  clean; mock build in progress (own `--uniqueext` chroot).

### hyprutils/hyprlang/hyprgraphics: version bumps, with a real lesson learned twice
`hyprland` needs newer versions of all three than what Fedora rawhide (and thus our earlier forks)
carry: `hyprutils` 0.7.1 -> 0.14.2, `hyprlang` 0.6.4 -> 0.6.8, `hyprgraphics` 0.1.5 -> 0.5.1 (exact
match to the floor). Before just bumping `Version:` and calling it done, checked each library's
*actual* CMakeLists.txt `SOVERSION` at the target tag directly (not assumed) - correctly caught
two real breaks this way:
- `hyprutils`: SOVERSION 6 -> 13. Fixed the hardcoded `%{_libdir}/lib%{name}.so.6` in `%files`.
- `hyprgraphics`: SOVERSION 0 -> 4. Fixed the hardcoded `%{_libdir}/libhyprgraphics.so.0`. Also
  confirmed its dependency list grew slightly (added `pangocairo`, `libpng`, dropped the `spng`
  dependency our 0.1.5 fork needed) - checked all new deps against el10 before proceeding.
- `hyprlang`: SOVERSION unchanged (2 at both versions) - no `%files` fix needed, just the version bump.

None of these three bumps have been mock-built yet as of this write-up (checks/edits done, builds
queued behind the currently-running `mir`/`lua` builds).

## Step 18 — hyprland AND miracle-wm both succeed: the session's capstone

Picking up from Step 17's status report (mir failing on a real GCC/C++ compile incompatibility,
hyprland.spec not yet written), user said simply "hyprland" - continued on both fronts in parallel.

### The systemic fix: gcc-toolset-15/16
Root cause behind mir's `std::optional<T>::value_or({...})` compile failures and (discovered next)
`hyprwire`'s `std::vector::append_range` failures: **el10's default GCC 14.4.1 has real libstdc++
completeness gaps** against C++23/26 standard library features these codebases use - not code bugs,
a genuine toolchain-version gap. Fixed with **`gcc-toolset-15`** (15.2.1) and later
**`gcc-toolset-16`** (16.2.1) - both official, opt-in newer-GCC packages already on el10 (RHEL's
standard mechanism for exactly this scenario), not COPR/third-party toolchains.

Getting this working cleanly took three real, distinct sub-fixes (each found via an actual failed
build, not anticipated):
1. `%enable_gcctoolset15` as a top-level spec macro fails with `Unknown tag` inside a **fresh** mock
   chroot - mock's own internal `rpmbuild -bs --nodeps` step parses the spec *before* any
   BuildRequires (including `gcc-toolset-15-runtime`, which ships the macro file) are installed.
   Fixed by sourcing `/usr/lib/gcc-toolset/15-env.source` directly as a shell command inside
   `%build` (and `%conf`, for mir's newer sectioned spec syntax - each section is its own shell
   invocation, so the env doesn't persist between them) instead of relying on the macro.
2. RPM's default hardening CFLAGS reference `-specs=.../redhat-annobin-cc1`, needing an annobin
   plugin matching whichever `cc1` actually runs - gcc-toolset's own `cc1` can't find the *system*
   GCC's plugin. Fixed with `gcc-toolset-15-gcc-plugin-annobin`.
3. GCC 15 itself wasn't new enough for hyprland specifically: `std::ranges::starts_with` (a newer
   C++23 range algorithm than `append_range`) isn't in GCC 15's libstdc++ either - confirmed via a
   real failed build AND a direct trivial-program compile test before committing to the bump.
   GCC 16.2.1 handles it fine. mir and hyprwire stayed on gcc-toolset-15 (sufficient for their
   actual code); hyprland alone needed gcc-toolset-16.

### mir: real success
With `umockdev` + `python-dbusmock` (both forked, see below) and gcc-toolset-15, **mir built
successfully in 13m37s of real compilation** - the first time in this whole thread of work. Copied
into the local repo, queued to real COPR (build 11031169) - **succeeded there too**.

### python-dbusmock: the second "unconditional at configure time" surprise
Same class of mistake as `umockdev` (Step 15's Step 15... see prior entry): assumed
`python3-dbusmock` was test-execution-only per Fedora's own "# For the tests" comment, made it
conditional on `run_tests`, got a real failed build (`ModuleNotFoundError: No module named
'dbusmock'`) proving Mir's CMake configure does a Python import check unconditionally too. Also
corrected a naming mistake: the dist-git repo is `python-dbusmock` (not `python3-dbusmock`, which
is only the built binary RPM's name) - the earlier "doesn't exist in Fedora" claim was from
checking the wrong path entirely.

### hyprwire: another genuinely from-scratch package, needed for hyprctl
Reading hyprland's own `hyprctl/CMakeLists.txt` before writing `hyprland.spec` surfaced a
dependency on `pkgconfig(hyprwire)` - a small IPC wire-protocol library, checked and confirmed to
not exist in Fedora, Terra, or anywhere else. Written from scratch following this repo's
aquamarine/hyprwayland-scanner conventions (same org, same CMake idioms - a lib plus an internal
`scanner` subdirectory). Hit the append_range issue here first (Step above), then built clean.

### hyprland.spec: written from scratch, the capstone of the whole session
No reference spec exists anywhere for hyprland itself (Fedora: 404 everywhere; Terra: deliberately
removed, "doesn't build anymore"). Two upstream dependencies needed vendoring rather than
packaging separately, both researched and resolved cleanly:
- **glaze** (header-only C++ JSON lib): hyprland's own CMakeLists.txt already has a FetchContent
  fallback for "not found" - rather than fight that, vendored the exact release tarball and pointed
  `FETCHCONTENT_SOURCE_DIR_GLAZE` at a locally-extracted copy in `%prep`, so FetchContent resolves
  it locally instead of hitting the network (mock/COPR builds have none in `%build`).
- **udis86**: hyprland falls back to `add_subdirectory(subprojects/udis86)` (a git submodule, not
  in GitHub's release tarball) if no system udis86 is found. Fetched the *exact* pinned submodule
  commit (`canihavesomecoffee/udis86` @ `5336633`, found via GitHub's tree API against the release
  tag) and vendored it directly - simpler and more certain than trying to satisfy the
  pkg_check_modules/find_library fallback chain with a separately-packaged Fedora udis86 (which
  doesn't ship a pkgconfig file anyway, so wouldn't even satisfy the first check).

Real, distinct build failures fixed in sequence, each from an actual attempt, not anticipated:
1. **udis86 nesting bug**: `subprojects/udis86` already exists as an *empty* directory in the
   release tarball (the git submodule's placeholder, content excluded but the dir itself isn't) -
   a plain `mv <extracted> subprojects/udis86` nests content one level too deep inside the existing
   dir instead of replacing it. Confirmed via `rpmbuild -bp --nodeps` + inspecting the actual
   extracted tree, not guessed. Fixed with `tar --strip-components=1 -C subprojects/udis86`
   (extracting *into* the existing placeholder) instead of extract-then-move.
2. **append_range**, fixed with gcc-toolset-15 (see above).
3. **A real pkg-config syntax bug in hyprland's own CMakeLists.txt**: its Lua detection list is
   `pkg_search_module(LUA REQUIRED ... lua55 lua5.5 lua-55 lua-5.5 lua>=5.5 lua<5.6)` - the last two
   candidates are dead on arrival, because pkg-config parses `lua>=5.5` (no spaces around the
   operator) as a *literal package name* to look up, not "lua" + a version constraint - confirmed
   directly by testing the exact query against our own `lua.pc` (`pkg-config --exists 'lua>=5.5'`
   genuinely looks for a file named `lua>=5.5.pc`). So hyprland actually depends on one of the
   *plain* candidate names resolving instead. Fixed by adding a `lua5.5.pc -> lua.pc` symlink to
   `specs/lua/` (one line in `%install`, wildcard `%files` picked it up automatically).
4. **starts_with**, fixed by bumping to gcc-toolset-16 (see above).
5. **Missed a local-repo sync step**: `aquamarine`'s first successful mock build (queued straight
   to COPR at the time) was never copied into the local `built-rpms/` repo used for further local
   mock testing - caught via a real failed build (`nothing provides pkgconfig(aquamarine)`), fixed
   by copying it in (a process-hygiene mistake, not a spec bug).
6. **Incomplete `%files`**: missing `hyprpm`'s shell completions and the `hyprland-uwsm.desktop`
   session file - caught via `error: Installed (but unpackaged) file(s) found` *after* the actual
   compile had already succeeded (confirmed real progress, not another compile-stage failure).

**Final result: `hyprland` built clean in mock (8m39s), installed locally alongside its full custom
dependency chain, and succeeded on real COPR (build 11031343).**

### Confirmed, not-forced: the lua conflict is real and now hits more than one package
Installing `hyprland` locally alongside its dependencies hit the exact `lua`/el10-`lua-libs`
conflict flagged in Step 17/PLAN.md - and confirmed it also affects **`wireplumber-libs`** (audio,
not just `ibus-libpinyin`/`brlapi`), a far more commonly-installed package. Did not force this with
`--allowerasing` on `durin`. This remains a real, unresolved packaging-strategy question (rename to
a side-by-side `lua5.5` package vs. accept the conflict vs. something else) that needs a decision
before this ships broadly - the mock build success proves the *package* is correct; it doesn't
resolve what happens when a real user with wireplumber/ibus-libpinyin installs it.

### Session status: everything explicitly requested this session is done
- `hyprland` - ✅ real COPR build succeeded (11031343)
- `miracle-wm` - ✅ real COPR build succeeded (11031307), depended on `mir` - ✅ also succeeded
  (11031169)
- All supporting packages discovered along the way (`aquamarine`, `hyprwire`, `hyprland-protocols`,
  `umockdev`, `python-dbusmock`, `rust-calloop`, `rust-input`, `rust-input-sys`, version bumps to
  `hyprutils`/`hyprlang`/`hyprgraphics`/`libxkbcommon`/`lua`) - all ✅ succeeded on real COPR.

**Open items for later, not blockers for what was asked**: the lua/wireplumber conflict (needs a
decision), `mangowm` (still blocked on the pixman/xkbcommon system bump decision from Step 14, not
touched further), `dms-greeter`'s real greetd chain already shipped, the actual `dnf copr enable
kmf/dank-ws-copr && dnf install ...` end-user flow hasn't been validated on a machine other than
`durin` yet, and `copr-cli` package-tracking (SCM-based auto-rebuild-on-push) vs. manual
`copr-cli build` per release hasn't been decided (Open Question 1 in PLAN.md).

## Next steps (not yet done)
- Actually install/smoke-test dms + dms-greeter + quickshell end-to-end on this host to validate
  the existing avengemedia builds work as a stack (Open Question #3).
- Re-check the `lionheartp/Hyprland` and `yalter/niri` COPR pages directly for el10/CentOS-Stream-10
  build targets (PLAN.md's "Related Links") rather than relying only on what's locally enabled.
- Decide CI trigger model and dms/dms-git shipping scope (Open Questions #1–2) now that the
  dependency landscape above is clearer.
