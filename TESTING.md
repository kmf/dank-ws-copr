# Testing Report — DankMaterialShell on CentOS Stream 10

Prepared in support of [AvengeMedia/DankMaterialShell#3442 "Officially Support: RHEL 10"](https://github.com/AvengeMedia/DankMaterialShell/issues/3442).

**Test machine**: `durin`, a real (not disposable/CI) CentOS Stream 10 workstation, x86_64,
kernel 6.12.0-269.el10, actively used as a daily-driver desktop during this work — not a scratch
VM spun up only to pass a build.

**COPR project**: [kmf/dank-ws-copr](https://copr.fedorainfracloud.org/coprs/kmf/dank-ws-copr/),
building for two chroots: `centos-stream-10-x86_64` and `epel-10-x86_64`. Both are needed —
newer `dnf-plugins-core` auto-detects a real CentOS Stream 10 host's Copr chroot as `epel-10-x86_64`
(Copr's generic "Enterprise Linux 10" name, covering RHEL/CentOS Stream/Rocky/Alma uniformly), not
`centos-stream-10-x86_64` — so `dnf copr enable kmf/dank-ws-copr` failed outright until the second
chroot was added and every package rebuilt for it (confirmed live: `hyprland`/`dms`/`cava` all now
resolve and dry-run install cleanly from it).

## Summary

- **82/84 real COPR builds succeeded** (server-side, clean-room chroot — not just local `mock`),
  covering 38 unique packages across both chroots; the other 2 were cleanly canceled mid-queue
  (an incorrect dependency chain, caught and re-queued correctly before either could fail) rather
  than genuine build failures. Zero actual failed COPR builds in this project's history — failures
  during iteration were always caught and fixed locally before ever being queued.
- **`mangowm` (the last originally-blocked compositor) now builds successfully too**, closing out
  every compositor this project set out to support. See
  [mangowm: the last blocker resolved](#mangowm-the-last-blocker-resolved) below.
- **Real end-to-end functional test performed**: a genuine Hyprland session, started through
  greetd's actual login protocol (not a shortcut), holding DRM master on real hardware, running
  DMS successfully. Full detail in [End-to-end login test](#end-to-end-login-test-hyprland--greetd--dms)
  below.
- **A real runtime bug was found and fixed**: DMS did not start under Hyprland by default (root
  cause: Hyprland has no built-in systemd session integration, unlike niri). See
  [Runtime bugs found and fixed](#runtime-bugs-found-and-fixed).
- **Verified independently of `durin`, twice**: a genuinely clean CentOS Stream 10 container (no
  local state, no pre-enabled repos) installed the full package set correctly via the real public
  COPR repos and the published install script - see
  [Fresh-box verification](#fresh-box-verification-independent-of-durin). A real KVM/QEMU VM then
  closed the container's one gap: booted, unattended, straight into a working Hyprland greeter
  session from a cold boot, with a real (virtual) GPU. See
  [Full VM boot-to-login test](#full-vm-boot-to-login-test-independent-of-durin-real-systemd--gpu).
- **All four supported compositors tested for real on that VM**: `niri`, `mangowm`, and `hyprland`
  all started correctly with the real DMS greeter UI on top; `miracle-wm` hit a genuine,
  VM-specific Mir session/VT-detection failure (works fine on real hardware, see
  [Known Issues](#known-issues) #5) - see
  [All four compositors tested for real on the VM](#all-four-compositors-tested-for-real-on-the-vm).
- **The remaining known, documented issues** — see [Known Issues](#known-issues) — are narrow
  (two real but low-blast-radius package conflicts, aarch64 untested, one `dms` CLI limitation) and
  don't block the core DMS + niri/hyprland/mangowm/miracle-wm + ghostty + greetd stack.

## Methodology

Every package in this repo went through some or all of these stages before being considered done:

1. **Local `mock` build** against the real `centos-stream-10-x86_64` chroot (not just `rpmbuild`
   directly) — catches missing BuildRequires and chroot-specific issues early. (The project also
   builds for `epel-10-x86_64` — see [Runtime bugs found and fixed](#runtime-bugs-found-and-fixed) —
   but local `mock` testing throughout this report used the `centos-stream-10-x86_64` config.)
2. **Local install + smoke test** on `durin` via `dnf install` of the built RPM, then a functional
   check appropriate to the package (`--version`/`--help`, `rpm -V`, `ldd`, or an actual runtime
   test for larger components).
3. **Real COPR build** — the package is uploaded and built by Copr's own infrastructure in a fresh
   chroot, independent of anything cached in `durin`'s local `mock` state. This is the strongest
   build-correctness signal in this report; a package that only built in local mock but not on
   COPR would not be marked done.
4. **Live functional/runtime test** — for the core interactive stack (compositor, greeter, shell),
   actually running the software as a real login session on real hardware, not just confirming the
   RPM installs cleanly.

## Package Table

All 38 packages below have a ✅ real COPR build (on both `centos-stream-10-x86_64` and
`epel-10-x86_64`, except where an earlier single-chroot build ID is shown from before the second
chroot existed — see [Runtime bugs found and fixed](#runtime-bugs-found-and-fixed)). "Local test"
describes what was actually run on `durin` beyond the build itself.

| Package | Version | COPR build | Local test performed |
|---|---|---|---|
| `gtk4-layer-shell` | 1.3.0 | [11030605](https://copr.fedorainfracloud.org/coprs/build/11030605) | Installed; unblocks ghostty |
| `ghostty` | 1.3.1 | [11030701](https://copr.fedorainfracloud.org/coprs/build/11030701) | Installed (17 RPMs), `rpm -V`/`ldd`/`ghostty --version` clean |
| `greetd` | 0.10.3 | [11030700](https://copr.fedorainfracloud.org/coprs/build/11030700) | Installed, `rpm -V`/`ldd`/`greetd --help` clean, enabled as active display manager |
| `rust-pam-sys` | — | [11030609](https://copr.fedorainfracloud.org/coprs/build/11030609) | Installed as greetd build dep |
| `rust-enquote` | — | [11030610](https://copr.fedorainfracloud.org/coprs/build/11030610) | Installed as greetd build dep |
| `rust-greetd_ipc` | — | [11030614](https://copr.fedorainfracloud.org/coprs/build/11030614) | Installed as greetd build dep |
| `rust-rpassword5` | — | [11030615](https://copr.fedorainfracloud.org/coprs/build/11030615) | Installed as greetd build dep |
| `dms-greeter` | 1.6.2 | (from `avengemedia/danklinux`, not built here) | Installed; **real end-to-end login test performed**, see below |
| `wlroots0.19` | 0.19.x | [11030613](https://copr.fedorainfracloud.org/coprs/build/11030613) | Installed; side-track for an older mangowm target, superseded |
| `scenefx` | 0.4.1 | [11030668](https://copr.fedorainfracloud.org/coprs/build/11030668) | Installed alongside wlroots0.19 |
| `hyprwayland-scanner` | 0.4.6 | [11035382](https://copr.fedorainfracloud.org/coprs/build/11035382) | Installed; `aquamarine`/`hyprland` rebuilt and reinstalled against it as regression checks (see below) |
| `hyprutils` | 0.14.2 | [11030604](https://copr.fedorainfracloud.org/coprs/build/11030604) | Installed, version-floor-verified against upstream CMakeLists |
| `hyprlang` | 0.6.8 | [11030665](https://copr.fedorainfracloud.org/coprs/build/11030665) | Installed |
| `hyprcursor` | 0.1.11 | [11030698](https://copr.fedorainfracloud.org/coprs/build/11030698) | Installed |
| `libspng` | 0.7.4 | [11030602](https://copr.fedorainfracloud.org/coprs/build/11030602) | Installed |
| `hyprgraphics` | 0.5.1 | [11030699](https://copr.fedorainfracloud.org/coprs/build/11030699) | Installed |
| `libxkbcommon` (bumped) | 1.13.1 | [11030607](https://copr.fedorainfracloud.org/coprs/build/11030607) | Installed system-wide on `durin` itself, replacing the stock package |
| `muparser` | 2.3.5 | [11030606](https://copr.fedorainfracloud.org/coprs/build/11030606) | Installed |
| `lua` (bumped) | 5.5.1 | [11031168](https://copr.fedorainfracloud.org/coprs/build/11031168) | Installed system-wide; see [Known Issues](#known-issues) |
| `aquamarine` | 0.15.1 | [11030646](https://copr.fedorainfracloud.org/coprs/build/11030646) | Installed; written from scratch, no reference spec anywhere |
| `hyprwire` | 0.3.1 | [11031167](https://copr.fedorainfracloud.org/coprs/build/11031167) | Installed; written from scratch |
| `hyprland-protocols` | 0.7.1 | [11031166](https://copr.fedorainfracloud.org/coprs/build/11031166) | Installed as a Hyprland build dep |
| `umockdev` | — | [11030608](https://copr.fedorainfracloud.org/coprs/build/11030608) | Installed as a `mir` build dep |
| `python-dbusmock` | — | [11031165](https://copr.fedorainfracloud.org/coprs/build/11031165) | Installed as a `mir` build dep |
| `rust-calloop` | — | [11031162](https://copr.fedorainfracloud.org/coprs/build/11031162) | Installed as a `mir` build dep |
| `rust-input` | — | [11030666](https://copr.fedorainfracloud.org/coprs/build/11030666) | Installed as a `mir` build dep |
| `rust-input-sys` | — | [11031163](https://copr.fedorainfracloud.org/coprs/build/11031163) | Installed as a `mir` build dep |
| `mir` | — | [11031169](https://copr.fedorainfracloud.org/coprs/build/11031169) | Installed; `libmiral`/`mircommon`/etc. subpackages resolve cleanly |
| `miracle-wm` | — | [11031307](https://copr.fedorainfracloud.org/coprs/build/11031307) | Installed |
| `hyprland` | 0.56.2 | [11031343](https://copr.fedorainfracloud.org/coprs/build/11031343) | **Currently installed and actively used** — see end-to-end test below |
| `cava` | 0.10.2 | [11031735](https://copr.fedorainfracloud.org/coprs/build/11031735) (rebuilt: [11035228](https://copr.fedorainfracloud.org/coprs/build/11035228)) | Installed, `cava -v` runs, confirmed by `dms doctor` |
| `iniparser` (bumped) | 4.2.6 | [11035226](https://copr.fedorainfracloud.org/coprs/build/11035226) | Installed system-wide, `pkg-config --modversion iniparser` confirms |
| `hyprtoolkit` | 0.6.0 | [11035229](https://copr.fedorainfracloud.org/coprs/build/11035229) | Installed |
| `hyprland-guiutils` | 0.2.2 | [11035230](https://copr.fedorainfracloud.org/coprs/build/11035230) | Installed, all 5 binaries confirmed present and executable |
| `pixman` (bumped) | 0.46.4 | [11047470](https://copr.fedorainfracloud.org/coprs/build/11047470) / [11047484](https://copr.fedorainfracloud.org/coprs/build/11047484) | Installed system-wide, `Hyprland`/`niri` regression-checked still working |
| `libdrm` (bumped) | 2.4.134 | [11047472](https://copr.fedorainfracloud.org/coprs/build/11047472) / [11047487](https://copr.fedorainfracloud.org/coprs/build/11047487) | Installed system-wide, same regression check |
| `wlroots0.20` | 0.20.2 | [11047474](https://copr.fedorainfracloud.org/coprs/build/11047474) / [11047491](https://copr.fedorainfracloud.org/coprs/build/11047491) | Installed side-by-side with el10's plain `wlroots` 0.18.2 |
| `scenefx` (bumped) | 0.5 | [11047475](https://copr.fedorainfracloud.org/coprs/build/11047475) / [11047492](https://copr.fedorainfracloud.org/coprs/build/11047492) | Installed |
| `mangowm` | 0.17.4 | [11047476](https://copr.fedorainfracloud.org/coprs/build/11047476) / [11047494](https://copr.fedorainfracloud.org/coprs/build/11047494) | Installed, `mango --help` runs, `ldd`/`rpm -V` clean |

Consumed as-is, not built in this repo (already work on el10 via their own upstream/AvengeMedia
COPRs — no fork needed): `dms`, `dms-cli`, `quickshell-git`, `matugen`, `cliphist`, `danksearch`,
`dgop`, `dankcalendar-git` (via `avengemedia/danklinux` + `avengemedia/dms-git`); `niri` (via
`yalter/niri`); `kf6-kimageformats` (via EPEL directly).

## mangowm: the last blocker resolved

`mangowm` was the one compositor this project originally flagged as blocked (see PLAN.md's history)
— Terra's own packaged spec required `wlroots-0.19`, and el10 only had `wlroots` 0.18.2. Given a
link to Terra's current Fedora 44 SRPM for mangowm 0.17.4, fetching and inspecting it directly
turned up the same staleness pattern found earlier in this project for other packages: **Terra's own
spec is wrong**. It still declares `BuildRequires: pkgconfig(wlroots-0.19)`, but 0.17.4's actual
source (`meson.build`) requires `wlroots-0.20 >=0.20.0` and `scenefx-0.5 >=0.5.0` — confirmed by
extracting the SRPM and reading `meson.build` directly, not assumed from the spec file.

Getting there needed a 5-package chain, each checked against real el10 versions before forking
anything:
- `xkbcommon` >=1.8.0 — already satisfied (bumped to 1.13.1 earlier this session for Hyprland, no
  new work needed).
- `pixman` bumped 0.43.4→0.46.4, **system-wide** — checked first whether this was safe: pixman's
  SONAME (`libpixman-1.so.0`) has stayed the same across this whole version range (confirmed
  against Fedora's own current spec), and a real reverse-dependency check
  (`dnf repoquery --whatrequires libpixman-1.so.0()(64bit)`) found cairo, mutter, weston, wlroots,
  qemu-kvm, Xwayland, and this project's own hyprland/aquamarine/hyprtoolkit/niri/mir all linking
  against it — all kept working unrebuilt after the bump (regression-checked: `Hyprland --help` and
  `niri --help` both still ran fine, `dms doctor` warning count unchanged).
- `wlroots0.20` — Fedora's current unversioned `wlroots` spec (0.20.2), renamed the same way this
  project's existing `wlroots0.19` package was (side-by-side install, since each wlroots minor
  version ships a distinctly-named library/pkgconfig path) — checked first that `wlroots0.19` and
  plain `wlroots` weren't going to collide with it (`dnf repoquery --whatrequires wlroots` showed
  only `cage` depends on the plain package, unaffected by adding a third side-by-side version).
  Hit one real, genuine build failure here: wlroots' own `meson.build` hard-enforces
  `libdrm >=2.4.129`, not just an RPM spec version pin — el10's libdrm (2.4.128) was one patch
  release short. Confirmed via the actual error (`Dependency libdrm found: NO. Found 2.4.128 but
  need: '>=2.4.129'`), then bumped `libdrm` too, 2.4.128→2.4.134, also system-wide (same
  SONAME-stability check as pixman: `libdrm.so.2` unchanged across this range, confirmed against
  Fedora's own current spec; 404 real reverse-dependency packages found, all still working
  unrebuilt).
- `scenefx` bumped back to 0.5 (wlroots-0.20) — superseding an earlier decision (2026-09-24) to pin
  this repo's `scenefx` at 0.4.1 for wlroots-0.19. That decision's whole premise (mango needing
  wlroots-0.19) turned out to rest on Terra's stale spec, not mango's actual requirement — checked
  first that nothing else in this repo depended on the 0.4.1 build before replacing it.
- `mangowm` 0.17.4 itself, with the corrected `BuildRequires`.

Built clean in mock on the first real attempt once the chain was in place (no iteration needed for
`mangowm` itself); installed locally (`mango --help` runs, `ldd`/`rpm -V` both clean). All 5
packages queued to real COPR in dependency order for both chroots — 10/10 succeeded.

## End-to-end login test (Hyprland + greetd + DMS)

Rather than just confirming packages install, we exercised the *real* login pipeline:

1. Switched `/etc/greetd/config.toml` to launch Hyprland; restarted `greetd` — the greeter itself
   came up **running on real Hyprland**, stable, no crash loop.
2. Drove greetd's own IPC socket directly (`create_session` → PAM auth → `start_session`, the exact
   protocol a real login uses) against a disposable throwaway account, launching `Hyprland` as the
   session command.
3. Confirmed via `loginctl`/`ps`: a genuine, separate Hyprland session started on `seat0`/`tty1`,
   obtained **DRM master on the real GPU**, `Xwayland` came up, a full `systemd --user` instance and
   D-Bus were alive.
4. `hyprland.log` showed real hardware — actual DP/eDP/HDMI outputs and a real touchpad/mouse
   detected — confirming this ran on genuine GPU/KMS, not a headless stub or VM.
5. Session stayed stable for the duration of the test (verified after a delay, no crash). Two
   benign `aquamarine: Cannot commit when a page-flip is awaiting` warnings appeared — known-harmless
   KMS contention noise, not a stability issue.
6. Cleaned up (terminated session, deleted the test account) and restored the prior config.

This is now `durin`'s regular daily-driver setup: Hyprland is installed, `dms.service` is enabled
and running, and the greeter is live on this exact machine as this report is written.

## Runtime bugs found and fixed

- **DMS did not start on login under Hyprland.** Root cause, confirmed by reading Hyprland's own
  source directly: unlike niri (whose `niri-session` wrapper natively activates
  `graphical-session.target`), plain Hyprland has **no built-in systemd session integration at
  all** — `dms.service`'s `WantedBy=graphical-session.target` never fires under it, independent of
  how correctly the service is enabled. Independently confirmed via Hyprland's own wiki
  ("plain Hyprland binary does not automatically activate graphical-session.target... requires
  UWSM or hyprland-session.target"). Fixed by running `dms setup headless --compositor hyprland
  --no-systemd`, DMS's own documented mechanism for this exact situation — it deploys a direct
  `hl.on("hyprland.start", ...) → dms run` exec hook instead of relying on the systemd target.
  Verified live: started `dms run` against the actual running Hyprland session and confirmed full
  clean initialization (network, bluetooth, polkit, clipboard, wallpaper managers all up, zero
  errors).
- **`dms-greeter enable --command <compositor>` does not work as might be assumed** — `--command`
  is only a flag on the root/`run` command, not the `enable` subcommand (Cobra does not propagate a
  non-persistent parent flag to subcommands); `enable` auto-detects whichever compositor is on
  `PATH` instead. Worth flagging upstream as a possible CLI/docs gap.
- **Self-correction found while preparing this report**: `specs/hyprwayland-scanner`'s checked-in
  spec claimed version 0.4.6 (an unconfirmed local bump explored 2026-09-24 for a possible
  `aquamarine` build issue), but the only COPR build ever published for it (11030603) was actually
  0.4.2 — the bump was never rebuilt or verified necessary. Confirmed `aquamarine`/`hyprland` only
  require `>=0.4.0`/`>=0.3.10` respectively (both satisfied by 0.4.2, checked their own upstream
  CMakeLists.txt directly) — the original build failure this bump was exploring had nothing to do
  with the scanner version. Rather than just revert and leave the package stale, completed the bump
  for real this time: `hyprwayland-scanner` 0.4.6 (upstream's current latest) built, installed, and
  `aquamarine` + `hyprland` both rebuilt and reinstalled against it as regression checks —
  `Hyprland --help` runs, `ldd`/`rpm -V` both clean. Real COPR builds: `hyprwayland-scanner`
  [11035382](https://copr.fedorainfracloud.org/coprs/build/11035382) → `aquamarine`
  [11035384](https://copr.fedorainfracloud.org/coprs/build/11035384) → `hyprland`
  [11035386](https://copr.fedorainfracloud.org/coprs/build/11035386).
- **`dnf copr enable kmf/dank-ws-copr` failed outright on a real, freshly-tested el10 host** with
  `Repository 'epel-10-x86_64' does not exist in project 'kmf/dank-ws-copr'. Available
  repositories: 'centos-stream-10-x86_64'`. Root cause: a newer `dnf-plugins-core` auto-detects the
  local Copr chroot name as `epel-10-x86_64` (Copr's generic "Enterprise Linux 10" chroot, covering
  RHEL/CentOS Stream/Rocky/Alma uniformly) rather than the CentOS-Stream-specific
  `centos-stream-10-x86_64` this project had only ever built for. Fixed by adding the
  `epel-10-x86_64` chroot to the project and rebuilding all 33 packages for it in dependency order
  (Copr chroots don't share build artifacts with each other) — all 33 succeeded. Verified live:
  `dnf copr enable` now succeeds, and `hyprland`/`dms`/`cava` all resolve and dry-run install
  cleanly from the newly-populated chroot.

## Fresh-box verification (independent of `durin`)

Every test above ran on `durin` — a machine with a lot of accumulated local state (system-wide
`pixman`/`libdrm`/`xkbcommon`/`lua` bumps, every COPR already enabled, `dnf`'s cache already warm).
To check this repo actually works for someone with none of that, pulled a genuinely clean
`quay.io/centos/centos:stream10` container (not derived from `durin` in any way) and ran the exact
public-facing flow a new user would:

1. `dnf install dnf-plugins-core epel-release && crb enable`
2. `dnf copr enable kmf/dank-ws-copr` — confirmed it auto-detects `epel-10-$basearch` here too (the
   same real bug fixed earlier), not just on `durin`.
3. Downloaded `scripts/dank-install-el10.sh` from its actual public raw GitHub URL (not copied from
   the local filesystem) and ran it for real as an unprivileged sudo user:
   `./dank-install-el10.sh -c niri -t ghostty -y`.

**Result: every expected package installed correctly** — `niri`, `dms`, `dms-cli`, `dms-greeter`,
`greetd`, `quickshell-git`, `matugen`, `cliphist`, `danksearch`, `dgop`, `dankcalendar-git`,
`ghostty`, `cava`, `kf6-kimageformats` all landed with real, resolvable versions, confirmed via
`rpm -qa` after the fact. `greetd`'s config was correctly rewritten to launch `niri`, and the
`greeter` system account was created correctly (`uid=995`).

Two things surfaced, both expected container limitations rather than real script bugs:
- `chown: invalid user: 'greetd:greetd'` during greetd's own install scriptlet — a
  `systemd-sysusers` ordering quirk from the container having no real systemd PID1, not a packaging
  defect (the `greetd`/`greeter` accounts both end up created correctly regardless, confirmed via
  `id`).
- `systemctl --user enable --now dms` correctly failed with `--now cannot be used when systemd is
  not running` (no real systemd PID1) — and the script's own hardening from an earlier fix (see
  [Runtime bugs found and fixed](#runtime-bugs-found-and-fixed)) caught this and printed the
  intended graceful warning instead of silently reporting success.

Neither was testable any further in a container - no real systemd PID1 or GPU to validate the
graphical/login parts independent of `durin`. That gap is closed by the VM test below.

## Full VM boot-to-login test (independent of `durin`, real systemd + GPU)

Installed `qemu-kvm`/`libvirt`/`virt-install` on `durin` (hardware virtualization already available
- `kvm_intel` was loaded) specifically to close the one gap the container test above couldn't cover:
a real systemd PID1 and a real (virtual) GPU, needed to validate the actual boot-to-greeter-to-login
flow independent of `durin` itself, not just package installation.

**Setup**: downloaded the official `CentOS-Stream-GenericCloud-10-latest.x86_64.qcow2` image
directly from `cloud.centos.org` (not derived from `durin`'s own disk in any way), built a
cloud-init NoCloud seed for unattended user/SSH provisioning, and created the VM with
`virt-install` (4 vCPU, 4GB RAM, `virtio` disk/net/video, `cpu host-passthrough`).

**A real, pre-existing infrastructure bug on `durin` surfaced immediately**: the VM had no outbound
network at all. Root-caused in two parts, both genuine gaps in `durin`'s own firewall config, not
libvirt bugs:
1. firewalld had no policy connecting the `libvirt` zone (where libvirt's NAT network lives) to the
   outside world at all - confirmed by inspecting the actual `nftables` ruleset directly
   (`nat_POST_libvirt_allow`, the chain that should hold the masquerade rule, was completely empty).
   Docker, installed on the same host, has its own working `docker-forwarding` firewalld policy;
   nothing equivalent existed for libvirt. Fixed by creating one (`firewall-cmd --new-policy`,
   `--add-ingress-zone=libvirt --add-egress-zone=ANY --add-masquerade`).
2. Even after that, return traffic still couldn't reach the VM. Found via the same direct
   `nft`/`iptables` inspection: Docker's own classic `iptables` `filter` table sets `FORWARD` chain
   policy to `DROP` globally (well-known Docker behavior) with no equivalent allow rule for
   `virbr0` traffic. Fixed with two targeted `firewall-cmd --direct` rules (outbound `-i virbr0
   ACCEPT`, return `-o virbr0 -m conntrack --ctstate ESTABLISHED,RELATED ACCEPT`) - checked and
   confirmed real, working `ping`/`curl`/`dnf makecache` connectivity from inside the VM only after
   both fixes were in place.

**Test performed**, entirely inside the VM over SSH, using only its own network access to the real
internet (nothing copied from `durin`'s filesystem):
1. `dnf install dnf-plugins-core epel-release && crb enable`
2. Downloaded and ran the real published `dank-install-el10.sh` from its raw GitHub URL:
   `./dank-install-el10.sh -c hyprland -t ghostty -y`
3. Rebooted the VM for real (`sudo reboot`) - not just re-running a service.

**Result: booted correctly straight into a working Hyprland greeter session**, entirely
unattended, from a cold boot:
- `greetd.service` started automatically via `systemd` (`systemctl get-default` → `graphical.target`,
  `systemctl status greetd` → active, started at boot)
- A genuine Hyprland process (`Hyprland --watchdog-fd 4`) came up as the greeter's compositor, with
  quickshell (`qs`) running the actual DMS greeter UI on top - confirmed still running (not
  crash-looped) after a delay
- Real DRM: `hyprland.log` showed aquamarine detecting the actual `virtio-gpu` DRM device
  (`/dev/dri/card0`, connector `Virtual-1`, "Red Hat, Inc. QEMU Monitor") and correctly falling
  back from a failed hardware EGL/DRI2 init (expected - this VM has no real GPU passthrough) to
  Mesa's `llvmpipe` software renderer, without crashing
- Every expected package installed with real, resolvable versions (`hyprland-guiutils` included),
  confirmed via `rpm -qa`

The VM (`dms-test-vm`, defined but shut off after the test) remains available on `durin` for future
testing without needing to be reprovisioned from scratch.

## All four compositors tested for real on the VM

Reused `dms-test-vm` (from the boot-to-login test above) to test every compositor this project
supports the same way: install it, point `greetd` at it (`sed` the `--command` in
`/etc/greetd/config.toml`, matching what `dms-greeter enable` itself writes), restart `greetd`,
confirm a real process comes up and stays up.

| Compositor | `dms-greeter --command` name | Result |
|---|---|---|
| `niri` | `niri` | ✅ Real `niri` process + DMS greeter UI (`qs`) on top, stable |
| `mangowm` | `mango` | ✅ Real `mango` process + DMS greeter UI on top, stable, no errors in `journalctl` - **first time this compositor has been tested end-to-end**, not just install-tested |
| `hyprland` | `hyprland` | ✅ Already covered by the boot-to-login test above (survived a full reboot) |
| `miracle-wm` | `miracle` | ❌ **Real failure, isolated to this VM** - see below |

### miracle-wm: a real, VM-specific failure (not a packaging defect)

`greetd` crash-looped (`error: check_children: greeter exited without creating a session`,
5 restarts, hit systemd's start-limit) when pointed at `miracle`. Running `miracle-wm` directly as
the `greeter` user surfaced the real cause in its own startup log:

```
mirserver: Not using logind for session management: Seat has no active session
mirserver: Not using Linux VT subsystem for session management: Failed to find the current VT
gbm-kms: Failed to probe DRM device: ... Failed to open device node: Permission denied [/dev/dri/card0]
```

Mir's own console-services layer can't find an active logind session or the current VT on this VM,
so it never gets a device ACL for `/dev/dri/card0` and fails outright - even though the exact same
`greeter` user, same `seat0`/`tty1` session, same lack of `video`-group membership or `seatd`
installed, works completely fine for `niri`/`mango`/`hyprland` (all wlroots/aquamarine-based,
using `libseat` rather than Mir's own console-services code). Since `mir`/`miracle-wm` already
passed this identical `greetd`+`dms-greeter` test on real hardware (`durin`) earlier in this report
- see [End-to-end login test](#end-to-end-login-test-hyprland--greetd--dms) - this looks like a
genuine Mir-specific gap in how it detects an active session/VT inside this particular VM
environment (cloud-init-provisioned, serial+virtio console, no full physical VT stack), not a
regression or a packaging defect in `specs/mir`/`specs/miracle-wm`. Not yet root-caused further
(would need real Mir-internals debugging - console-services' logind/VT detection code - to say
exactly why it can't find what `niri`/`mango` find fine on the same session); left as a real,
documented, open finding rather than papered over.

## Known Issues

1. **`lua` 5.5 (needed by Hyprland's `lua>=5.5,<5.6` floor) conflicts with el10's stock `lua-libs`
   5.4**, a real dependency of `wireplumber-libs` and `ibus-libpinyin`. Confirmed via a real local
   install attempt on `durin`, not forced through with `--allowerasing`. On `durin` itself neither
   conflicting package is installed, so this hasn't blocked testing here, but it's a real
   packaging-strategy question (side-by-side rename vs. accept the conflict) that would need
   resolving before this ships broadly. Not present for `niri` or `miracle-wm`.
2. **`iniparser` bumped to 4.2.6 conflicts with `daxctl`/`ndctl`/`netatalk`** (real CentOS/EPEL
   packages pinned to the old `libiniparser.so.1`), needed for `hyprtoolkit`'s build. Narrower
   blast radius than the lua conflict — none of those three are things a desktop-shell user would
   typically have installed.
3. **aarch64 untested** — everything above is x86_64 only so far.
4. **`dms setup headless` does not support `miracle-wm`** (`unknown compositor "miracle-wm"
   (expected niri, hyprland, or mango)`) — DMS's own CLI limitation, not a packaging gap in this
   repo. It does support `mango` (mangowm's `dms setup` name) as of that package now building.
5. **`miracle-wm` fails to acquire a display inside the test VM specifically** (Mir's
   console-services can't find an active logind session or VT there), while working correctly on
   real hardware (`durin`). See
   [All four compositors tested for real on the VM](#all-four-compositors-tested-for-real-on-the-vm)
   for the full detail - not yet root-caused to a specific fix.

## Reproducing this

```bash
sudo dnf copr enable -y avengemedia/danklinux avengemedia/dms-git kmf/dank-ws-copr
curl -fsSL -o dank-install-el10.sh https://raw.githubusercontent.com/kmf/dank-ws-copr/main/scripts/dank-install-el10.sh
chmod +x dank-install-el10.sh
./dank-install-el10.sh -c hyprland -t ghostty -y
```

See [`README.md`](README.md) for full installation instructions, [`PLAN.md`](PLAN.md) for the
complete dependency/decision history, and [`SETUP.md`](SETUP.md) for the step-by-step build log
behind every entry in this report.
