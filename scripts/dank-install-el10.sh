#!/usr/bin/env bash
#
# dank-install-el10.sh - unofficial installer for DankMaterialShell on
# CentOS Stream 10 / RHEL 10 / EPEL10, modeled on AvengeMedia's own
# `dankinstall` (curl -fsSL https://install.danklinux.com | sh) which does
# not support RHEL/CentOS at all today.
#
# Flag-driven only (v1) - no interactive menu, mirrors dankinstall's
# documented headless mode: `-c niri -t ghostty -y`.
#
# Sources used, per kmf/dank-ws-copr's PLAN.md/SETUP.md:
#   - avengemedia/danklinux COPR : quickshell, matugen, cliphist, danksearch,
#                                  dgop, dankcalendar-git, dms-greeter (all
#                                  confirmed working on el10 unmodified)
#   - avengemedia/dms-git COPR   : the `dms` package itself (only channel
#                                  populated for el10 today - no stable
#                                  avengemedia/dms el10 builds exist yet)
#   - yalter/niri COPR           : niri (confirmed installs cleanly on el10
#                                  as-is; we do not fork it)
#   - kmf/dank-ws-copr           : everything we had to fork/build ourselves
#                                  (hyprland, mir, miracle-wm, ghostty,
#                                  greetd + its rust crate chain, and the
#                                  hyprland dependency chain)
#
# Known open issue (see specs/lua/lua.spec and PLAN.md): hyprland pulls in
# our rebuilt `lua` 5.5, which conflicts with el10's stock lua-libs 5.4 -
# a real dependency of wireplumber-libs and ibus-libpinyin. This script
# refuses to proceed with --compositor hyprland if it detects either
# installed, unless --force is given.
#
# When --no-greeter isn't passed, this script also runs `dms-greeter enable`
# and then patches /etc/greetd/config.toml if it didn't auto-detect the
# compositor we actually asked for (mapping miracle-wm -> dms-greeter's own
# "miracle" name; --command is not a valid flag on the `enable` subcommand
# itself - see the inline comment at the call site) and, if gdm is enabled,
# disables it and enables greetd in its place - without this, gdm silently
# keeps winning the display-manager.service alias
# at boot even after greetd is installed and configured.

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
COMPOSITOR="niri"
TERMINAL="ghostty"
INSTALL_GREETER=1
ENABLE_SERVICE=1
ASSUME_YES=0
DRY_RUN=0
FORCE=0

OUR_COPR="kmf/dank-ws-copr"
DANKLINUX_COPR="avengemedia/danklinux"
DMS_COPR="avengemedia/dms-git"
NIRI_COPR="yalter/niri"

CORE_PACKAGES=(quickshell-git matugen cliphist danksearch dgop dankcalendar-git)
DMS_PACKAGE="dms"
GREETER_PACKAGE="dms-greeter"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
red() { printf '\033[0;31m%s\033[0m\n' "$*"; }
green() { printf '\033[0;32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[1;33m%s\033[0m\n' "$*"; }

die() {
    red "Error: $*"
    exit 1
}

run() {
    if [ "$DRY_RUN" = "1" ]; then
        printf '[dry-run] %s\n' "$*"
    else
        "$@"
    fi
}

usage() {
    cat <<'EOF'
dank-install-el10.sh - install DankMaterialShell on CentOS Stream 10 / RHEL 10

Usage:
  dank-install-el10.sh [options]

Options:
  -c, --compositor NAME   Compositor to install: niri (default), hyprland, miracle-wm
  -t, --terminal NAME     Terminal to install: ghostty (default), kitty, alacritty
      --no-greeter        Skip installing dms-greeter / greetd
      --no-enable-service Skip enabling the dms systemd --user service
  -y, --yes               Assume yes on dnf prompts (non-interactive)
      --dry-run           Print the commands that would run without running them
      --force             Skip the el10 distro check and the known lua/hyprland
                           conflict guard (see script header)
      --menu              Force the interactive menu even if other flags are given
  -h, --help              Show this help and exit

Examples:
  # headless, matches upstream dankinstall's flag style
  sudo -v && ./dank-install-el10.sh -c niri -t ghostty -y

  # Hyprland instead, with kitty
  ./dank-install-el10.sh -c hyprland -t kitty -y

  # interactive menu (also runs automatically with no arguments)
  ./dank-install-el10.sh --menu
EOF
}

# ---------------------------------------------------------------------------
# Basic interactive menu - plain bash `select`, no dialog/whiptail dependency.
# Runs automatically when the script is invoked with no arguments at all, or
# explicitly via --menu. Everything downstream (repo/package/greeter logic)
# is unchanged - this just fills in the same variables flags would.
# ---------------------------------------------------------------------------
choose() {
    # choose <prompt> <option>...  - first option is the recommended/default
    # one (listed first, as "1)"); bash's `select` re-prompts on a blank
    # line rather than picking it automatically, so a real numeric choice
    # is required.
    local prompt="$1" reply
    shift
    local options=("$@")
    printf '\n%s\n' "$prompt" >&2
    PS3="> "
    select reply in "${options[@]}"; do
        if [ -n "$reply" ]; then
            printf '%s\n' "$reply"
            return 0
        fi
        echo "Invalid choice, try again." >&2
    done
}

confirm() {
    # confirm <prompt> <default y|n> -> returns 0 for yes, 1 for no
    local prompt="$1" default="$2" reply
    while true; do
        read -r -p "$prompt [$([ "$default" = y ] && echo Y/n || echo y/N)]: " reply
        reply="${reply:-$default}"
        case "$reply" in
        [Yy]*) return 0 ;;
        [Nn]*) return 1 ;;
        *) echo "Please answer y or n." >&2 ;;
        esac
    done
}

run_menu() {
    green "== dank-install-el10 interactive setup =="

    COMPOSITOR=$(choose "Choose a compositor:" niri hyprland miracle-wm)
    TERMINAL=$(choose "Choose a terminal:" ghostty kitty alacritty)

    if confirm "Install dms-greeter and set it as the login manager?" y; then
        INSTALL_GREETER=1
    else
        INSTALL_GREETER=0
    fi

    if confirm "Enable the dms systemd --user service after install?" y; then
        ENABLE_SERVICE=1
    else
        ENABLE_SERVICE=0
    fi

    if confirm "Proceed with dnf without further per-package confirmation (-y)?" y; then
        ASSUME_YES=1
    else
        ASSUME_YES=0
    fi

    printf '\n'
    green "Summary: compositor=$COMPOSITOR terminal=$TERMINAL greeter=$([ "$INSTALL_GREETER" = 1 ] && echo yes || echo no) service=$([ "$ENABLE_SERVICE" = 1 ] && echo yes || echo no) assume-yes=$([ "$ASSUME_YES" = 1 ] && echo yes || echo no)"
    confirm "Continue with these choices?" y || die "aborted at menu confirmation"
}

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------
FORCE_MENU=0
NO_ARGS=0
[ $# -eq 0 ] && NO_ARGS=1

while [ $# -gt 0 ]; do
    case "$1" in
    -c | --compositor)
        COMPOSITOR="$2"
        shift 2
        ;;
    -t | --terminal)
        TERMINAL="$2"
        shift 2
        ;;
    --no-greeter)
        INSTALL_GREETER=0
        shift
        ;;
    --no-enable-service)
        ENABLE_SERVICE=0
        shift
        ;;
    -y | --yes)
        ASSUME_YES=1
        shift
        ;;
    --dry-run)
        DRY_RUN=1
        shift
        ;;
    --force)
        FORCE=1
        shift
        ;;
    --menu)
        FORCE_MENU=1
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        die "Unknown option: $1 (see --help)"
        ;;
    esac
done

if [ "$NO_ARGS" = "1" ] || [ "$FORCE_MENU" = "1" ]; then
    run_menu
fi

case "$COMPOSITOR" in
niri | hyprland | miracle-wm) ;;
*) die "--compositor must be one of: niri, hyprland, miracle-wm (got: $COMPOSITOR)" ;;
esac

case "$TERMINAL" in
ghostty | kitty | alacritty) ;;
*) die "--terminal must be one of: ghostty, kitty, alacritty (got: $TERMINAL)" ;;
esac

DNF_YES_FLAG=()
[ "$ASSUME_YES" = "1" ] && DNF_YES_FLAG=(-y)

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
[ "$(id -u)" = "0" ] && die "do not run this script as root; it uses sudo where needed"

command -v dnf >/dev/null 2>&1 || die "dnf not found - this script is for CentOS Stream 10 / RHEL 10 / EPEL10 only"

if [ "$FORCE" != "1" ]; then
    . /etc/os-release 2>/dev/null || die "cannot read /etc/os-release"
    case "${PLATFORM_ID:-}" in
    platform:el10) ;;
    *)
        die "this script targets el10 (CentOS Stream 10 / RHEL 10), detected PLATFORM_ID='${PLATFORM_ID:-unset}'. Use --force to override."
        ;;
    esac
fi

if [ "$COMPOSITOR" = "hyprland" ] && [ "$FORCE" != "1" ]; then
    conflicting=()
    for pkg in wireplumber-libs ibus-libpinyin; do
        rpm -q "$pkg" >/dev/null 2>&1 && conflicting+=("$pkg")
    done
    if [ "${#conflicting[@]}" -gt 0 ]; then
        red "Known conflict: --compositor hyprland requires our rebuilt lua-5.5, which"
        red "collides with el10's stock lua-libs 5.4, a dependency of: ${conflicting[*]}"
        red "This is a documented, unresolved packaging issue (see specs/lua/lua.spec and"
        red "PLAN.md in kmf/dank-ws-copr). Re-run with --force to proceed anyway, or pick"
        red "--compositor niri or --compositor miracle-wm instead."
        exit 1
    fi
fi

green "Installing DankMaterialShell for el10: compositor=$COMPOSITOR terminal=$TERMINAL"

# ---------------------------------------------------------------------------
# Repos
# ---------------------------------------------------------------------------
run sudo dnf install "${DNF_YES_FLAG[@]}" epel-release
run sudo dnf config-manager --set-enabled crb
run sudo dnf install "${DNF_YES_FLAG[@]}" dnf-plugins-core copr-cli || true

run sudo dnf copr enable "${DNF_YES_FLAG[@]}" "$DANKLINUX_COPR"
run sudo dnf copr enable "${DNF_YES_FLAG[@]}" "$DMS_COPR"
run sudo dnf copr enable "${DNF_YES_FLAG[@]}" "$OUR_COPR"

if [ "$COMPOSITOR" = "niri" ]; then
    run sudo dnf copr enable "${DNF_YES_FLAG[@]}" "$NIRI_COPR"
fi

# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------
run sudo dnf install "${DNF_YES_FLAG[@]}" "${CORE_PACKAGES[@]}"
run sudo dnf install "${DNF_YES_FLAG[@]}" "$COMPOSITOR"
run sudo dnf install "${DNF_YES_FLAG[@]}" "$TERMINAL"
run sudo dnf install "${DNF_YES_FLAG[@]}" "$DMS_PACKAGE"

if [ "$INSTALL_GREETER" = "1" ]; then
    run sudo dnf install "${DNF_YES_FLAG[@]}" "$GREETER_PACKAGE"

    # dms-greeter's own compositor names don't all match our package/compositor
    # names (notably miracle-wm -> miracle).
    case "$COMPOSITOR" in
    miracle-wm) GREETER_COMMAND="miracle" ;;
    *) GREETER_COMMAND="$COMPOSITOR" ;;
    esac

    # NOTE: `--command` is only a flag on dms-greeter's root/`run` command,
    # not on the `enable` subcommand (Cobra doesn't propagate a non-persistent
    # parent flag to subcommands) - `dms-greeter --command X enable` hard
    # fails with "unknown flag: --command". `enable` instead auto-detects
    # whichever compositor is on PATH and writes it straight into
    # /etc/greetd/config.toml's `command =` line itself, so it must be run
    # plain, then patched below if it didn't pick what we actually want.
    GREETER_ENABLE_FLAGS=(enable)
    [ "$ASSUME_YES" = "1" ] && GREETER_ENABLE_FLAGS+=(-y)
    run sudo dms-greeter "${GREETER_ENABLE_FLAGS[@]}"

    GREETD_CONFIG=/etc/greetd/config.toml
    if [ "$DRY_RUN" = "1" ]; then
        printf '[dry-run] ensure %s runs "dms-greeter --command %s" in %s\n' "$GREETER_COMMAND" "$GREETER_COMMAND" "$GREETD_CONFIG"
    elif [ -f "$GREETD_CONFIG" ] && ! grep -q -- "--command $GREETER_COMMAND" "$GREETD_CONFIG"; then
        yellow "dms-greeter enable configured a different compositor than requested; fixing $GREETD_CONFIG"
        sudo sed -i -E "s/--command [A-Za-z_-]+/--command $GREETER_COMMAND/" "$GREETD_CONFIG"
    fi

    # `dms-greeter enable` wires up greetd's own config but does not fight
    # gdm for the display-manager.service alias - only one unit can hold it,
    # so gdm (if present and enabled) silently keeps winning at boot unless
    # explicitly disabled here.
    if systemctl list-unit-files gdm.service >/dev/null 2>&1 && systemctl is-enabled --quiet gdm.service 2>/dev/null; then
        run sudo systemctl disable gdm.service
        run sudo systemctl enable greetd.service
    fi
fi

# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
if [ "$ENABLE_SERVICE" = "1" ]; then
    if [ "$DRY_RUN" = "1" ]; then
        printf '[dry-run] systemctl --user enable --now dms\n'
    else
        systemctl --user enable --now dms || yellow "Could not enable dms --user service now; enable it after your next login."
    fi
fi

if [ "$INSTALL_GREETER" = "1" ]; then
    green "Done. Reboot to land on the dms-greeter/greetd login screen defaulting to '$COMPOSITOR'."
else
    green "Done. Log out and select '$COMPOSITOR' from your display/login manager's session list."
fi
if [ "$COMPOSITOR" = "hyprland" ]; then
    yellow "Note: hyprland here depends on our rebuilt lua-5.5 (see script header) - watch for"
    yellow "conflicts if you later install wireplumber-libs or ibus-libpinyin."
fi
