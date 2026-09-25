# dank-ws-copr

<div align="center">

  ### DankMaterialShell packages for CentOS Stream 10 / RHEL 10 / EPEL10

  Compositors, terminal, and the full dependency chain — built with [COPR](https://copr.fedorainfracloud.org/)

[![COPR Build](https://img.shields.io/badge/COPR-kmf%2Fdank--ws--copr-73ba25?labelColor=101418)](https://copr.fedorainfracloud.org/coprs/kmf/dank-ws-copr/)
[![CentOS Stream 10](https://img.shields.io/badge/CentOS_Stream-10-262577?labelColor=101418)](https://www.centos.org/centos-stream/)
[![License](https://img.shields.io/badge/license-various-b9c8da?labelColor=101418)](specs/NOTICE.md)

</div>

[AvengeMedia's `danklinux`](https://github.com/AvengeMedia/danklinux) packages DankMaterialShell for
Debian, Ubuntu, Fedora, and openSUSE. This repo covers the distro they don't: CentOS Stream 10 /
RHEL 10 / EPEL10. Where AvengeMedia's own COPR (`avengemedia/danklinux`, `avengemedia/dms-git`)
already has working el10 builds, we consume those directly — this repo only exists to fill the real
gaps: compositors and dependency chains that needed forking, patching, or building entirely from
scratch to work on el10.

## Available Packages

### Compositors
- **hyprland** — dynamic tiling Wayland compositor, built from scratch (no reference spec existed anywhere)
- **mir** / **miracle-wm** — Mir-based tiling compositor
- **niri** — not packaged here; installs cleanly straight from [`yalter/niri`](https://copr.fedorainfracloud.org/coprs/yalter/niri/), no fork needed

### Terminal
- **ghostty** — GPU-accelerated terminal emulator

### Hyprland dependency chain
`aquamarine`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics`, `hyprwayland-scanner`,
`hyprwire`, `hyprland-protocols`, `gtk4-layer-shell`, `libxkbcommon` (bumped), `lua` (bumped),
`muparser`, `libspng`

### Hyprland GUI utilities
- **hyprland-guiutils** — dialog/file-picker/crash-reporter/welcome screens Hyprland shells out to;
  genuinely unpackaged anywhere upstream (not even Fedora)
- **hyprtoolkit** — Hyprland's own native (non-Qt) GUI toolkit, required by the above
- `iniparser` (bumped) — needed a pkgconfig file `hyprtoolkit`'s build requires; el10's own didn't
  ship one

### Greeter
- **greetd** + `dms-greeter` — includes 4 forked Rust crate dependencies (`rust-pam-sys`,
  `rust-enquote`, `rust-greetd_ipc`, `rust-rpassword5`)

### Mir toolkit dependencies
`umockdev`, `python-dbusmock`, `rust-calloop`, `rust-input`, `rust-input-sys`

### Optional features (surfaced by `dms doctor`)
- **cava** — audio visualizer
- `kimageformats` isn't packaged here — it ships directly from EPEL as `kf6-kimageformats`

## Installation

> **Full details, open issues, and the complete build log**: see [`PLAN.md`](PLAN.md) and
> [`SETUP.md`](SETUP.md) in this repo.

### One-line install script

[`scripts/dank-install-el10.sh`](scripts/dank-install-el10.sh) is an unofficial equivalent of
AvengeMedia's own `dankinstall` (`curl -fsSL https://install.danklinux.com | sh`), which doesn't
support RHEL/CentOS at all. It enables the right repos, installs your chosen compositor and
terminal, deploys DMS's compositor config integration (`dms setup headless`), sets up `dms` +
`dms-greeter`, and enables the DMS systemd user service.

```bash
curl -fsSL -o dank-install-el10.sh https://raw.githubusercontent.com/kmf/dank-ws-copr/main/scripts/dank-install-el10.sh
chmod +x dank-install-el10.sh

# headless, matches upstream dankinstall's flag style
sudo -v && ./dank-install-el10.sh -c niri -t ghostty -y

# or run with no arguments for an interactive menu
./dank-install-el10.sh
```

### Manual installation (CentOS Stream 10 / RHEL 10)

```bash
# 1. Dependencies (EPEL + CRB, plus AvengeMedia's own working el10 repos)
sudo dnf install -y epel-release
sudo dnf config-manager --set-enabled crb
sudo dnf copr enable -y avengemedia/danklinux
sudo dnf copr enable -y avengemedia/dms-git

# 2. This repo, for everything AvengeMedia doesn't build for el10
sudo dnf copr enable -y kmf/dank-ws-copr

# 3. Core shell
sudo dnf install -y quickshell-git matugen cliphist danksearch dgop dankcalendar-git dms

# 4. A compositor - niri comes from its own upstream COPR, not this repo
sudo dnf copr enable -y yalter/niri
sudo dnf install -y niri
# or: sudo dnf install -y hyprland hyprland-guiutils   /   sudo dnf install -y miracle-wm

# 5. Terminal, greeter, optional extras
sudo dnf install -y ghostty dms-greeter cava kf6-kimageformats

# 6. Deploy the compositor config integration - installing `dms` alone does NOT
# do this. Required for niri/hyprland (not yet supported for miracle-wm);
# --no-systemd is required for hyprland specifically, since unlike niri it has
# no built-in systemd session integration (dms.service would otherwise never
# start under it - see PLAN.md's hyprland entry).
dms setup headless --compositor niri --no-systemd --terminal ghostty
# or: dms setup headless --compositor hyprland --no-systemd --terminal ghostty

# 7. Enable the greeter and the DMS service
sudo dms-greeter enable -y
systemctl --user enable --now dms
```

> **Known issue**: `hyprland` depends on our rebuilt `lua` 5.5, which conflicts with el10's stock
> `lua-libs` 5.4 — a real dependency of `wireplumber-libs` and `ibus-libpinyin`. See
> [`specs/lua/lua.spec`](specs/lua/lua.spec) and `PLAN.md`'s Known Blockers table. Not yet resolved;
> `dank-install-el10.sh` refuses to install hyprland if it detects either package unless `--force`
> is passed.

## Architecture Support

- **x86_64** — built and verified
- **aarch64** — not yet built or tested

## Upstream Projects

- [DankMaterialShell](https://github.com/AvengeMedia/DankMaterialShell) — DMS desktop environment
- [danklinux](https://github.com/AvengeMedia/danklinux) — DMS packages for Debian/Ubuntu/Fedora/openSUSE (the repo this one complements)
- [dank-greeter](https://github.com/AvengeMedia/dank-greeter) — greetd greeter (`dms-greeter`)
- [Hyprland](https://github.com/hyprwm/Hyprland) — dynamic tiling Wayland compositor
- [Mir](https://github.com/canonical/mir) / [miracle-wm](https://github.com/miracle-wm-org/miracle-wm) — Mir-based tiling compositor
- [Niri](https://github.com/YaLTeR/niri) — scrollable-tiling Wayland compositor (not packaged here, see above)
- [Ghostty](https://github.com/ghostty-org/ghostty) — terminal emulator
- [greetd](https://sr.ht/~kennylevinsen/greetd/) — minimal login manager daemon

## Build Status

- **COPR**: [kmf/dank-ws-copr](https://copr.fedorainfracloud.org/coprs/kmf/dank-ws-copr/), targeting `centos-stream-10-x86_64`
- **Dependencies (Tiers 1–3)**: [avengemedia/danklinux](https://copr.fedorainfracloud.org/coprs/avengemedia/danklinux/), [avengemedia/dms-git](https://copr.fedorainfracloud.org/coprs/avengemedia/dms-git/)
- **niri**: [yalter/niri](https://copr.fedorainfracloud.org/coprs/yalter/niri/) (upstream, not built here)

## Contributing

Packaging specs and automation maintained in this repository. Every fork/adaptation of a
third-party spec carries a header comment naming its exact source and what was changed; see
[`specs/NOTICE.md`](specs/NOTICE.md) for the full attribution index.

- **Packaging issues**: [GitHub Issues](https://github.com/kmf/dank-ws-copr/issues)
- **Upstream bugs**: report to the respective project repositories above

## License

This repo's own scripts and original specs (`hyprwire`, `aquamarine`, `hyprland`, `muparser`, and
others written from scratch) have no upstream license constraint beyond the packaged software's
own. Specs forked from [Terra EL](https://github.com/terrapkg/packages-el) retain that project's
GPL-3.0 license; specs forked from Fedora's dist-git retain their packaged software's own license
per standard Fedora packaging convention. See [`specs/NOTICE.md`](specs/NOTICE.md) for the
file-by-file breakdown.
