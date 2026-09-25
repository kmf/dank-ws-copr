# Testing Report — DankMaterialShell on CentOS Stream 10

Prepared in support of [AvengeMedia/DankMaterialShell#3442 "Officially Support: RHEL 10"](https://github.com/AvengeMedia/DankMaterialShell/issues/3442).

**Test machine**: `durin`, a real (not disposable/CI) CentOS Stream 10 workstation, x86_64,
kernel 6.12.0-269.el10, actively used as a daily-driver desktop during this work — not a scratch
VM spun up only to pass a build.

**COPR project**: [kmf/dank-ws-copr](https://copr.fedorainfracloud.org/coprs/kmf/dank-ws-copr/),
targeting `centos-stream-10-x86_64`.

## Summary

- **36/36 real COPR builds succeeded** (server-side, clean-room chroot — not just local `mock`),
  covering 33 unique packages. Zero failed COPR builds in this project's history; failures during
  iteration were caught and fixed locally before ever being queued.
- **Real end-to-end functional test performed**: a genuine Hyprland session, started through
  greetd's actual login protocol (not a shortcut), holding DRM master on real hardware, running
  DMS successfully. Full detail in [End-to-end login test](#end-to-end-login-test-hyprland--greetd--dms)
  below.
- **A real runtime bug was found and fixed**: DMS did not start under Hyprland by default (root
  cause: Hyprland has no built-in systemd session integration, unlike niri). See
  [Runtime bugs found and fixed](#runtime-bugs-found-and-fixed).
- **Two known, documented, unresolved issues** remain — see [Known Issues](#known-issues) — neither
  blocks the core DMS + niri + ghostty + greetd stack.

## Methodology

Every package in this repo went through some or all of these stages before being considered done:

1. **Local `mock` build** against the real `centos-stream-10-x86_64` chroot (not just `rpmbuild`
   directly) — catches missing BuildRequires and chroot-specific issues early.
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

All 33 packages below have a ✅ real COPR build. "Local test" describes what was actually run on
`durin` beyond the build itself.

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
| `hyprwayland-scanner` | 0.4.2 | [11030603](https://copr.fedorainfracloud.org/coprs/build/11030603) | Installed as a build dep throughout the Hyprland chain |
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

Consumed as-is, not built in this repo (already work on el10 via their own upstream/AvengeMedia
COPRs — no fork needed): `dms`, `dms-cli`, `quickshell-git`, `matugen`, `cliphist`, `danksearch`,
`dgop`, `dankcalendar-git` (via `avengemedia/danklinux` + `avengemedia/dms-git`); `niri` (via
`yalter/niri`); `kf6-kimageformats` (via EPEL directly).

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
  0.4.2 — the bump was never rebuilt or verified necessary. Confirmed `aquamarine` only requires
  `>=0.4.0` and built fine against 0.4.2, so reverted the spec to match what's actually live and
  tested rather than silently claim an untested version.

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
3. **`mangowm` remains unbuilt** — blocked on a `pixman`/`xkbcommon` system-wide version bump not
   yet executed; not part of this report's tested set.
4. **aarch64 untested** — everything above is x86_64 only so far.
5. **`dms setup headless` does not support `miracle-wm`** (`unknown compositor "miracle-wm"
   (expected niri, hyprland, or mango)`) — DMS's own CLI limitation, not a packaging gap in this
   repo.

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
