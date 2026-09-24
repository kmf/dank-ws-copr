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

## Next steps (not yet done)
- Actually install/smoke-test dms + dms-greeter + quickshell end-to-end on this host to validate
  the existing avengemedia builds work as a stack (Open Question #3).
- Re-check the `lionheartp/Hyprland` and `yalter/niri` COPR pages directly for el10/CentOS-Stream-10
  build targets (PLAN.md's "Related Links") rather than relying only on what's locally enabled.
- Decide CI trigger model and dms/dms-git shipping scope (Open Questions #1–2) now that the
  dependency landscape above is clearer.
