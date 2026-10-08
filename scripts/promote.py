#!/usr/bin/env python3
"""Promote baked builds from the rolling COPR to the stable COPR.

For every package in the rolling project this finds the newest version-release
that succeeded on all of the package's chroots at least `bake_days` ago, and if
it is newer than what stable has, rebuilds that exact SRPM (rolling's
srpm-builds URL) in the stable project. Builds are submitted as chained COPR
batches following the dependency waves in promotion.yaml.

Dry run by default; pass --apply to submit. Needs python3-copr and PyYAML and a
~/.config/copr (or --copr-config) for an account that can build in stable.
"""

import argparse
import os
import sys
import time
from collections import defaultdict

import yaml
from copr.v3 import Client

DAY = 86400
FINAL = {"succeeded", "failed", "canceled", "skipped", "forked"}
ACTIVE = {"pending", "starting", "running", "importing", "waiting"}


# --- rpm version comparison (rpmvercmp) -------------------------------------
def _segments(s):
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch == "~" or ch == "^":
            out.append(ch)
            i += 1
        elif ch.isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            out.append(int(s[i:j]))
            i = j
        elif ch.isalpha():
            j = i
            while j < len(s) and s[j].isalpha():
                j += 1
            out.append(s[i:j])
            i = j
        else:
            i += 1
    return out


def rpmvercmp(a, b):
    if a == b:
        return 0
    sa, sb = _segments(a), _segments(b)
    for x, y in zip(sa, sb):
        if x == y:
            continue
        for mark in ("~", "^"):
            if x == mark or y == mark:
                if mark == "~":
                    return -1 if x == "~" else 1
                return 1 if x == "^" else -1
        if isinstance(x, int) and isinstance(y, int):
            return 1 if x > y else -1
        if isinstance(x, int):
            return 1
        if isinstance(y, int):
            return -1
        return 1 if x > y else -1
    la, lb = len(sa), len(sb)
    if la == lb:
        return 0
    rest = (sa[lb:] if la > lb else sb[la:])[0]
    sign = 1 if la > lb else -1
    if rest == "~":
        return -sign
    return sign


def evr_cmp(a, b):
    def split(v):
        e, _, vr = v.rpartition(":") if ":" in v else ("0", "", v)
        ver, _, rel = vr.partition("-")
        return int(e or 0), ver, rel
    ea, va, ra = split(a)
    eb, vb, rb = split(b)
    if ea != eb:
        return 1 if ea > eb else -1
    return rpmvercmp(va, vb) or rpmvercmp(ra, rb)


# --- COPR inspection --------------------------------------------------------
def split_project(full):
    owner, name = full.split("/", 1)
    return owner, name


def project_state(client, full, chroots_of, deep):
    """Return {package: {version: info}} for a COPR project.

    info = {"ok": {chroot: first_success_ts}, "active": bool,
            "url": srpm url of the newest succeeded build, "url_build": id}
    `deep` queries per-chroot results of failed builds (partial successes).
    """
    owner, name = split_project(full)
    builds = client.build_proxy.get_list(owner, name, pagination={"limit": 10000})
    state = defaultdict(lambda: defaultdict(lambda: {"ok": {}, "active": False, "url": None, "url_build": 0}))
    for b in sorted(builds, key=lambda b: b.id):
        sp = b.source_package or {}
        pkg, ver = sp.get("name"), sp.get("version")
        if not pkg or not ver:
            continue
        info = state[pkg][ver]
        if b.state in ACTIVE:
            info["active"] = True
            continue
        ok_chroots = []
        if b.state == "succeeded":
            ok_chroots = [(ch, b.ended_on or b.submitted_on) for ch in b.chroots]
        elif b.state == "failed" and deep:
            for bc in client.build_chroot_proxy.get_list(b.id):
                if bc.state == "succeeded":
                    ok_chroots.append((bc.name, bc.ended_on or b.ended_on or b.submitted_on))
        for ch, ts in ok_chroots:
            if ch not in info["ok"] or ts < info["ok"][ch]:
                info["ok"][ch] = ts
        if ok_chroots and sp.get("url") and b.id > info["url_build"]:
            info["url"], info["url_build"] = sp["url"], b.id
    return state


def complete_versions(versions, chroots):
    """[(version, available_since_ts, info)] fully succeeded on `chroots`, newest first."""
    out = []
    for ver, info in versions.items():
        if all(ch in info["ok"] for ch in chroots):
            out.append((ver, max(info["ok"][ch] for ch in chroots), info))
    out.sort(key=lambda t: _Key(t[0]), reverse=True)
    return out


class _Key:
    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        return evr_cmp(self.v, other.v) < 0


# --- main -------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=os.path.join(here, "..", "promotion.yaml"))
    ap.add_argument("--copr-config", help="copr-cli config file (default ~/.config/copr)")
    ap.add_argument("--apply", action="store_true", help="submit builds (default: dry run)")
    ap.add_argument("--wait", action="store_true", help="with --apply, wait for the builds and fail if any fail")
    ap.add_argument("--bake-days", type=float, help="override bake_days (0 = seed stable with rolling's latest)")
    ap.add_argument("--packages", help="comma-separated subset of packages to consider")
    args = ap.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    bake_days = cfg.get("bake_days", 7) if args.bake_days is None else args.bake_days
    default_chroots = cfg["chroots"]
    overrides = cfg.get("packages") or {}
    holds = set(cfg.get("holds") or [])
    pins = {k: str(v) for k, v in (cfg.get("pins") or {}).items()}
    waves = [list(w) for w in cfg["waves"]]
    group_of = {}
    for g in cfg.get("groups") or []:
        for pkg in g:
            group_of[pkg] = list(g)
    only = set(args.packages.split(",")) if args.packages else None

    def chroots_of(pkg):
        return (overrides.get(pkg) or {}).get("chroots") or default_chroots

    client = Client.create_from_config_file(args.copr_config) if args.copr_config else Client.create_from_config_file()
    rolling = project_state(client, cfg["rolling"], chroots_of, deep=True)
    stable = project_state(client, cfg["stable"], chroots_of, deep=False)

    ordered = [p for w in waves for p in w]
    extra = sorted(set(rolling) - set(ordered))
    if extra:
        print(f"warning: not in promotion.yaml waves, appending to last wave: {', '.join(extra)}", file=sys.stderr)
        waves[-1].extend(extra)

    now = time.time()

    def group_ready(pkg):
        """True if every member's newest complete rolling build has baked (or is in stable)."""
        for m in group_of.get(pkg, [pkg]):
            if m not in rolling or m in holds:
                continue
            cands = complete_versions(rolling[m], chroots_of(m))
            if m in pins:
                cands = [c for c in cands if c[0] == pins[m]]
            if not cands:
                continue
            st = complete_versions(stable.get(m, {}), chroots_of(m))
            if st and evr_cmp(cands[0][0], st[0][0]) <= 0:
                continue
            if now - cands[0][1] < bake_days * DAY:
                return False
        return True

    plan = []      # (wave index, pkg, version, url)
    report = []    # (pkg, rolling newest, stable, decision)
    for wi, wave in enumerate(waves):
        for pkg in wave:
            if only and pkg not in only:
                continue
            if pkg not in rolling:
                report.append((pkg, "-", "-", "not on rolling"))
                continue
            chroots = chroots_of(pkg)
            cands = complete_versions(rolling[pkg], chroots)
            st = complete_versions(stable.get(pkg, {}), chroots)
            st_ver = st[0][0] if st else None
            newest = max(rolling[pkg], key=_Key)
            in_flight = [v for v, i in stable.get(pkg, {}).items() if i["active"]]
            row = lambda d: report.append((pkg, newest, st_ver or "-", d))
            if pkg in holds:
                row("held")
                continue
            if pkg in pins:
                cands = [c for c in cands if c[0] == pins[pkg]]
            baked = [c for c in cands if now - c[1] >= bake_days * DAY]
            if not baked:
                if cands:
                    left = bake_days - (now - cands[0][1]) / DAY
                    row(f"baking {cands[0][0]} ({left:.1f}d left)")
                else:
                    row("no build succeeded on all chroots" + (f" at pin {pins[pkg]}" if pkg in pins else ""))
                continue
            if pkg in group_of and not group_ready(pkg):
                row("waiting for group " + "+".join(group_of[pkg]) + " to bake")
                continue
            ver, since, info = baked[0]
            if st_ver and evr_cmp(ver, st_ver) <= 0:
                note = "up to date"
                if evr_cmp(newest, st_ver) > 0 and newest != ver:
                    note += f" ({newest} not yet promotable)"
                row(note)
                continue
            if ver in in_flight:
                row(f"{ver} already building in stable")
                continue
            age = (now - since) / DAY
            row(f"PROMOTE {ver} (baked {age:.1f}d, rolling build {info['url_build']})")
            plan.append((wi, pkg, ver, info["url"], chroots))

    w = max(len(r[0]) for r in report) if report else 10
    print(f"bake_days={bake_days}  {cfg['rolling']} -> {cfg['stable']}  ({'APPLY' if args.apply else 'dry run'})\n")
    print(f"{'package':<{w}}  {'rolling':<14}  {'stable':<14}  decision")
    for pkg, rv, sv, d in report:
        print(f"{pkg:<{w}}  {rv:<14}  {sv:<14}  {d}")
    print(f"\n{len(plan)} package(s) to promote")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(f"### COPR promotion ({'apply' if args.apply else 'dry run'}, bake_days={bake_days})\n\n")
            f.write("| package | rolling | stable | decision |\n|---|---|---|---|\n")
            for r in report:
                f.write("| " + " | ".join(r) + " |\n")

    if not args.apply or not plan:
        return 0

    owner, name = split_project(cfg["stable"])
    submitted = []
    prev_batch_build = None
    for wi in sorted({p[0] for p in plan}):
        first = None
        for _, pkg, ver, url, chroots in [p for p in plan if p[0] == wi]:
            opts = {"chroots": chroots}
            if first is not None:
                opts["with_build_id"] = first
            elif prev_batch_build is not None:
                opts["after_build_id"] = prev_batch_build
            b = client.build_proxy.create_from_url(owner, name, url, buildopts=opts)
            print(f"submitted wave {wi + 1}: {pkg} {ver} -> build {b.id}")
            submitted.append((pkg, ver, b.id))
            if first is None:
                first = b.id
        prev_batch_build = first

    if not args.wait:
        return 0
    print("\nwaiting for builds...")
    pending = {bid for _, _, bid in submitted}
    while pending:
        time.sleep(60)
        for bid in list(pending):
            if client.build_proxy.get(bid).state in FINAL:
                pending.discard(bid)
    failed = 0
    for pkg, ver, bid in submitted:
        res = {bc.name: bc.state for bc in client.build_chroot_proxy.get_list(bid)}
        bad = {k: v for k, v in res.items() if v != "succeeded"}
        failed += bool(bad)
        print(f"{pkg} {ver} build {bid}: " + ("succeeded" if not bad else f"FAILED {bad}"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
